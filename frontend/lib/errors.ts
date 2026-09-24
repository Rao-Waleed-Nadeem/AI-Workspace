export type ApiErrorPayload = {
  error?: {
    code?: string;
    message?: string;
    details?: unknown;
  };
  detail?: string;
};

export class ApiError extends Error {
  status: number;
  code: string;
  details?: unknown;

  constructor(
    message: string,
    status: number,
    code: string,
    details?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export async function createApiError(
  response: Response,
  fallbackMessage: string,
): Promise<ApiError> {
  let payload: ApiErrorPayload | null = null;

  try {
    payload = (await response.json()) as ApiErrorPayload;
  } catch {}

  const message =
    payload?.error?.message ??
    payload?.detail ??
    fallbackMessage;

  return new ApiError(
    message,
    response.status,
    payload?.error?.code ?? "request_error",
    payload?.error?.details,
  );
}