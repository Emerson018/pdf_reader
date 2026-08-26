const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface ChatResponse {
  response: string;
  conversation_id?: string;
  metadata?: Record<string, any>;
}

export interface UploadTaskResponse {
  task_id: string;
  filename: string;
  message: string;
}

export interface UploadStatusResponse {
  task_id: string;
  filename: string;
  status: 'processing' | 'completed' | 'failed';
  total_pages: number;
  current_page: number;
  progress_percent: number;
  elapsed_seconds: number;
  estimated_remaining_seconds: number;
  message: string;
}

export interface IngestedDocumentInfo {
  document_name: string;
  total_chunks: number;
  created_at: string | null;
}

export interface DocumentChunkInfo {
  id: number;
  document_name: string;
  chunk_index: number;
  content_preview: string;
  full_content: string;
  embedding_dim: number;
  metadata: Record<string, any>;
  created_at: string | null;
}

export interface RagMetricsResponse {
  timestamp: string;
  uptime_seconds: number;
  redis_cache: {
    status: string;
    total_cached_queries: number;
    hits: number;
    misses: number;
    total_requests: number;
    hit_rate_percent: number;
    avg_hit_latency_ms: number;
  };
  postgresql_vector_db: {
    status: string;
    total_documents: number;
    total_chunks: number;
    total_vision_chunks: number;
    vector_dimension: number;
    embedding_model: string;
    index_type: string;
    search_algorithms: string;
  };
  minio_storage: {
    status: string;
    bucket: string;
  };
  infrastructure_health: {
    api: string;
    postgres: string;
    redis: string;
    minio: string;
  };
}

export async function sendChatMessage(
  message: string,
  conversationId?: string
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP Error ${response.status}`);
  }

  return response.json();
}

export async function uploadPdfDocument(file: File, processImages: boolean = true): Promise<UploadTaskResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('process_images', String(processImages));

  const response = await fetch(`${API_BASE_URL}/api/v1/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Falha no upload do arquivo (HTTP ${response.status})`);
  }

  return response.json();
}

export async function getUploadStatus(taskId: string): Promise<UploadStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/documents/upload/status/${taskId}`, {
    method: 'GET',
    headers: {
      'Cache-Control': 'no-cache',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Falha ao consultar status (HTTP ${response.status})`);
  }

  return response.json();
}

export async function listIngestedDocuments(): Promise<IngestedDocumentInfo[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/documents`, {
    method: 'GET',
    headers: {
      'Cache-Control': 'no-cache',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Falha ao listar documentos (HTTP ${response.status})`);
  }

  return response.json();
}

export async function listDocumentChunks(documentName?: string): Promise<DocumentChunkInfo[]> {
  const url = documentName
    ? `${API_BASE_URL}/api/v1/documents/chunks?document_name=${encodeURIComponent(documentName)}`
    : `${API_BASE_URL}/api/v1/documents/chunks`;

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Cache-Control': 'no-cache',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Falha ao listar chunks do banco (HTTP ${response.status})`);
  }

  return response.json();
}

export async function getRagMetrics(): Promise<RagMetricsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/metrics/rag`, {
    method: 'GET',
    headers: {
      'Cache-Control': 'no-cache',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Falha ao carregar métricas RAG (HTTP ${response.status})`);
  }

  return response.json();
}

export async function exportRagReport(
  content: string,
  metadata?: Record<string, any>,
  format: 'markdown' | 'pdf' = 'markdown'
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/chat/export`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      content,
      metadata: metadata || {},
      format,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Falha ao exportar relatório (HTTP ${response.status})`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  const contentDisposition = response.headers.get('Content-Disposition');
  let filename = format === 'pdf' ? 'Relatorio_RAG.pdf' : 'Relatorio_RAG.md';
  if (contentDisposition) {
    const match = contentDisposition.match(/filename="?([^"]+)"?/);
    if (match && match[1]) {
      filename = match[1];
    }
  }
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}
