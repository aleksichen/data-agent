'use client'
import { useState } from 'react'
import { toast } from 'sonner'
import { TextArea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { usePlaygroundStore } from '@/workflow_store'
import useAIChatStreamHandler from '@/workflow_hooks/useAIStreamHandler'
import Icon from '@/components/ui/icon'

const ChatInput = () => {
  const { chatInputRef } = usePlaygroundStore()

  const { handleStreamResponse } = useAIChatStreamHandler()
  const [inputMessage, setInputMessage] = useState('')
  const isStreaming = usePlaygroundStore((state) => state.isStreaming)
  const handleSubmit = async () => {
    if (!inputMessage.trim()) return

    const currentMessage = inputMessage
    setInputMessage('')

    try {
      await handleStreamResponse(currentMessage)
    } catch (error) {
      toast.error(
        `Error in handleSubmit: ${
          error instanceof Error ? error.message : String(error)
        }`
      )
    }
  }

  return (
    <div className="font-geist relative mx-auto mb-1 flex w-full max-w-2xl items-end justify-center gap-x-2">
      <TextArea
        placeholder={'Ask anything'}
        value={inputMessage}
        onChange={(e) => setInputMessage(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey && !isStreaming) {
            e.preventDefault()
            handleSubmit()
          }
        }}
        className="border-accent bg-primaryAccent text-primary focus:border-accent w-full border px-4 text-sm"
        ref={chatInputRef}
      />
      <Button
        onClick={handleSubmit}
        disabled={!inputMessage.trim() || isStreaming}
        size="icon"
        className="bg-primary text-primaryAccent rounded-xl p-5"
      >
        <Icon type="send" color="primaryAccent" />
      </Button>
    </div>
  )
}

export default ChatInput
