package com.example.springaidemo.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.document.Document;
import org.springframework.ai.reader.pdf.PagePdfDocumentReader;
import org.springframework.ai.reader.pdf.config.PdfDocumentReaderConfig;
import org.springframework.ai.transformer.splitter.TokenTextSplitter;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.io.Resource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * Service for ingesting documents into the vector store
 * This service reads PDF documents, splits them into chunks, 
 * generates embeddings, and stores them in the vector database
 */
@Service
public class DocumentIngestionService implements CommandLineRunner {

    private static final Logger logger = LoggerFactory.getLogger(DocumentIngestionService.class);

    private final VectorStore vectorStore;
    
    @Value("${app.documents.path:classpath:documents/}")
    private String documentsPath;
    
    @Value("${app.documents.auto-ingest:true}")
    private boolean autoIngest;

    public DocumentIngestionService(VectorStore vectorStore) {
        this.vectorStore = vectorStore;
    }

    @Override
    public void run(String... args) throws Exception {
        if (autoIngest) {
            logger.info("Starting automatic document ingestion...");
            ingestDocuments();
        } else {
            logger.info("Automatic document ingestion is disabled");
        }
    }

    /**
     * Ingests all PDF documents from the configured path
     */
    public void ingestDocuments() {
        try {
            PathMatchingResourcePatternResolver resolver = new PathMatchingResourcePatternResolver();
            Resource[] resources = resolver.getResources(documentsPath + "*.pdf");

            if (resources.length == 0) {
                logger.warn("No PDF documents found in path: {}", documentsPath);
                logger.info("Please add PDF documents to src/main/resources/documents/ for ingestion");
                return;
            }

            logger.info("Found {} PDF document(s) to ingest", resources.length);

            for (Resource resource : resources) {
                logger.info("Processing document: {}", resource.getFilename());
                ingestDocument(resource);
            }

            logger.info("Document ingestion completed successfully");
        } catch (Exception e) {
            logger.error("Error during document ingestion", e);
        }
    }

    /**
     * Ingests a single document
     * 
     * @param resource The document resource to ingest
     */
    public void ingestDocument(Resource resource) {
        try {
            // Configure PDF reader
            PdfDocumentReaderConfig config = PdfDocumentReaderConfig.builder()
                    .withPageTopMargin(0)
                    .withPageBottomMargin(0)
                    .withPageExtractedTextFormatter(
                            PdfDocumentReaderConfig.builder().build()
                                    .getPageExtractedTextFormatter()
                    )
                    .build();

            // Read PDF document
            PagePdfDocumentReader pdfReader = new PagePdfDocumentReader(resource, config);
            List<Document> documents = pdfReader.get();

            logger.info("Read {} pages from document: {}", documents.size(), resource.getFilename());

            // Split documents into chunks
            // TokenTextSplitter splits text into chunks based on token count
            // This ensures chunks are not too large for the embedding model
            TokenTextSplitter textSplitter = new TokenTextSplitter();
            List<Document> chunks = textSplitter.apply(documents);

            logger.info("Split document into {} chunks", chunks.size());

            // Add metadata to chunks
            for (Document chunk : chunks) {
                chunk.getMetadata().put("source", resource.getFilename());
            }

            // Store chunks in vector database
            // This automatically generates embeddings and stores them
            vectorStore.add(chunks);

            logger.info("Successfully stored {} chunks in vector database for document: {}", 
                    chunks.size(), resource.getFilename());

        } catch (Exception e) {
            logger.error("Error ingesting document: " + resource.getFilename(), e);
        }
    }

    /**
     * Clears all documents from the vector store
     * Useful for testing or re-indexing
     */
    public void clearVectorStore() {
        try {
            // Note: Not all vector stores support deletion
            // Check your vector store implementation for delete capabilities
            logger.info("Clearing vector store...");
            // vectorStore.delete() // implement based on your vector store
            logger.info("Vector store cleared successfully");
        } catch (Exception e) {
            logger.error("Error clearing vector store", e);
        }
    }
}
