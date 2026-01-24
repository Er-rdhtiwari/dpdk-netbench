"""KB index building using LlamaIndex."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

import yaml
from llama_index.core import (
    Document,
    Settings,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from pypdf import PdfReader

from netbench.config import settings


class KBIndexBuilder:
    """Build and manage LlamaIndex vector index from PDF knowledge base."""

    def __init__(self, kb_path: Path, index_path: Path) -> None:
        """Initialize the index builder.

        Args:
            kb_path: Path to KB directory containing PDFs
            index_path: Path to store the vector index
        """
        self.kb_path = kb_path
        self.index_path = index_path
        self.manifest_path = kb_path / "manifest.yaml"

        # Configure LlamaIndex settings
        Settings.llm = OpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            api_base=settings.openai_api_base,
        )
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )
        Settings.chunk_size = settings.chunk_size
        Settings.chunk_overlap = settings.chunk_overlap

    def load_manifest(self) -> Dict[str, Any]:
        """Load KB manifest file.

        Returns:
            Manifest dictionary with PDF metadata
        """
        if not self.manifest_path.exists():
            return {"pdfs": [], "version": "1.0"}

        with open(self.manifest_path, "r") as f:
            return yaml.safe_load(f)

    def save_manifest(self, manifest: Dict[str, Any]) -> None:
        """Save KB manifest file.

        Args:
            manifest: Manifest dictionary to save
        """
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_path, "w") as f:
            yaml.dump(manifest, f, default_flow_style=False)

    def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extract text from PDF with page metadata.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of page dictionaries with text and metadata
        """
        reader = PdfReader(pdf_path)
        pages = []

        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text.strip():
                pages.append({
                    "page_num": page_num,
                    "text": text,
                    "source_file": pdf_path.name,
                })

        return pages

    def build_documents(self, pdf_metadata: Dict[str, Any]) -> List[Document]:
        """Build LlamaIndex documents from PDF.

        Args:
            pdf_metadata: PDF metadata from manifest

        Returns:
            List of LlamaIndex Document objects
        """
        pdf_path = self.kb_path / "pdfs" / pdf_metadata["filename"]
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        pages = self.extract_text_from_pdf(pdf_path)
        documents = []

        for page_data in pages:
            # Build metadata for each page
            metadata = {
                "source_file": pdf_metadata["filename"],
                "page_start": page_data["page_num"],
                "page_end": page_data["page_num"],
                "vendor": pdf_metadata.get("vendor", "unknown"),
                "platform": pdf_metadata.get("platform", "generic"),
                "version": pdf_metadata.get("version", "unknown"),
                "benchmark_tags": ",".join(pdf_metadata.get("benchmark_tags", [])),
                "epyc_family_tags": ",".join(pdf_metadata.get("epyc_family_tags", [])),
                "release_tags": ",".join(pdf_metadata.get("release_tags", [])),
            }

            doc = Document(
                text=page_data["text"],
                metadata=metadata,
                id_=f"{pdf_metadata['filename']}_page_{page_data['page_num']}",
            )
            documents.append(doc)

        return documents

    def compute_manifest_hash(self, manifest: Dict[str, Any]) -> str:
        """Compute hash of manifest for change detection.

        Args:
            manifest: Manifest dictionary

        Returns:
            SHA256 hash of manifest
        """
        manifest_str = json.dumps(manifest, sort_keys=True)
        return hashlib.sha256(manifest_str.encode()).hexdigest()

    def build_index(self, force_rebuild: bool = False) -> VectorStoreIndex:
        """Build or load the vector index.

        Args:
            force_rebuild: Force rebuild even if index exists

        Returns:
            LlamaIndex VectorStoreIndex
        """
        manifest = self.load_manifest()
        manifest_hash = self.compute_manifest_hash(manifest)

        # Check if we can load existing index
        hash_file = self.index_path / "manifest_hash.txt"
        if not force_rebuild and self.index_path.exists() and hash_file.exists():
            with open(hash_file, "r") as f:
                stored_hash = f.read().strip()

            if stored_hash == manifest_hash:
                print("Loading existing index (manifest unchanged)...")
                storage_context = StorageContext.from_defaults(persist_dir=str(self.index_path))
                return load_index_from_storage(storage_context)

        # Build new index
        print("Building new index from PDFs...")
        all_documents = []

        for pdf_meta in manifest.get("pdfs", []):
            print(f"Processing: {pdf_meta['filename']}")
            documents = self.build_documents(pdf_meta)
            all_documents.extend(documents)

        if not all_documents:
            raise ValueError("No documents found to index. Add PDFs to data/kb/pdfs/ and update manifest.yaml")

        # Create index with sentence splitter
        splitter = SentenceSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        index = VectorStoreIndex.from_documents(
            all_documents,
            transformations=[splitter],
            show_progress=True,
        )

        # Persist index
        self.index_path.mkdir(parents=True, exist_ok=True)
        index.storage_context.persist(persist_dir=str(self.index_path))

        # Save manifest hash
        with open(hash_file, "w") as f:
            f.write(manifest_hash)

        print(f"Index built successfully with {len(all_documents)} documents")
        return index

    def add_pdf(
        self,
        pdf_path: Path,
        vendor: str,
        platform: str,
        version: str,
        benchmark_tags: List[str],
        epyc_family_tags: List[str],
        release_tags: List[str],
    ) -> None:
        """Add a new PDF to the KB and update manifest.

        Args:
            pdf_path: Path to PDF file
            vendor: Vendor name (e.g., "AMD")
            platform: Platform name (e.g., "EPYC")
            version: Document version
            benchmark_tags: List of benchmark tags (e.g., ["cryptoperf", "testpmd"])
            epyc_family_tags: List of EPYC family tags (e.g., ["7003", "9004"])
            release_tags: List of release tags
        """
        # Copy PDF to kb/pdfs/
        dest_path = self.kb_path / "pdfs" / pdf_path.name
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if not dest_path.exists():
            import shutil
            shutil.copy(pdf_path, dest_path)

        # Update manifest
        manifest = self.load_manifest()

        # Check if PDF already exists
        existing = [p for p in manifest.get("pdfs", []) if p["filename"] == pdf_path.name]
        if existing:
            print(f"PDF {pdf_path.name} already in manifest, updating metadata...")
            manifest["pdfs"] = [p for p in manifest["pdfs"] if p["filename"] != pdf_path.name]

        manifest.setdefault("pdfs", []).append({
            "filename": pdf_path.name,
            "vendor": vendor,
            "platform": platform,
            "version": version,
            "benchmark_tags": benchmark_tags,
            "epyc_family_tags": epyc_family_tags,
            "release_tags": release_tags,
        })

        self.save_manifest(manifest)
        print(f"Added {pdf_path.name} to manifest. Run 'make index' to rebuild.")

# Made with Bob
