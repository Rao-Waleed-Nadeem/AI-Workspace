# Fix: SSE Streaming & chat_id Propagation

## Steps

- [x] 1. **Plan created and approved**

- [ ] 2. **Backend: Send `chat_id` as first SSE event in `stream_response`**
  - File: `backend/app/services/chat_service.py`
  - After creating a new chat, yield `data: {"chat_id": <id>}\n\n` before streaming tokens.

- [ ] 3. **Frontend: Fix SSE parsing in `api.ts`**
  - File: `frontend/lib/api.ts`
  - Accept `onChatId` callback.
  - Properly parse SSE: split by `\n\n`, strip `data: `, check JSON for `chat_id`, call `onChatId` or `onChunk` accordingly.

- [ ] 4. **Frontend: Wire `onChatId` in `page.tsx`**
  - File: `frontend/app/page.tsx`
  - Pass `onChatId={(id) => setChatId(id)}` to `sendMessage`.

- [ ] 5. **Test the fixes**
