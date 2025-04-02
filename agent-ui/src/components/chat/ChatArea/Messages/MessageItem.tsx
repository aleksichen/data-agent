import Icon from '@/components/ui/icon'
import MarkdownRenderer from '@/components/ui/typography/MarkdownRenderer'
import { usePlaygroundStore } from '@/workflow_store'
import type { PlaygroundChatMessage } from '@/types/playground'
import Videos from './Multimedia/Videos'
import Images from './Multimedia/Images'
import Audios from './Multimedia/Audios'
import { memo } from 'react'
import AgentThinkingLoader from './AgentThinkingLoader'
import { Chart, ChartProps } from '../../charts'

interface MessageProps {
  message: PlaygroundChatMessage
}

const chartData = [
  { month: 'Jan', sales: 100, profit: 50, category: 'A', customers: 120 },
  { month: 'Feb', sales: 120, profit: 60, category: 'A', customers: 130 },
  { month: 'Mar', sales: 140, profit: 70, category: 'A', customers: 150 },
  { month: 'Apr', sales: 160, profit: 80, category: 'A', customers: 170 },
  { month: 'May', sales: 180, profit: 90, category: 'A', customers: 165 },
  { month: 'Jun', sales: 200, profit: 100, category: 'A', customers: 180 },
  { month: 'Jan', sales: 80, profit: 40, category: 'B', customers: 100 },
  { month: 'Feb', sales: 90, profit: 45, category: 'B', customers: 110 },
  { month: 'Mar', sales: 100, profit: 50, category: 'B', customers: 120 },
  { month: 'Apr', sales: 110, profit: 55, category: 'B', customers: 125 },
  { month: 'May', sales: 120, profit: 60, category: 'B', customers: 130 },
  { month: 'Jun', sales: 130, profit: 65, category: 'B', customers: 140 }
]

const AgentMessage = ({ message }: MessageProps) => {
  const { streamingErrorMessage } = usePlaygroundStore()

  let messageContent
  if (message.streamingError) {
    messageContent = (
      <p className="text-destructive">
        Oops! Something went wrong while streaming.{' '}
        {streamingErrorMessage ? (
          <>{streamingErrorMessage}</>
        ) : (
          'Please try refreshing the page or try again later.'
        )}
      </p>
    )
  } else if (message.content_type === 'chart' && message.content) {
    const chartConfig: ChartProps = JSON.parse(message.content) as ChartProps
    console.log(chartConfig)
    messageContent = (
      <>
        <Chart {...chartConfig} data={chartConfig.data || chartData} />
      </>
    )
  } else if (message.content) {
    messageContent = (
      <div className="flex w-full flex-col gap-4">
        <MarkdownRenderer>{message.content}</MarkdownRenderer>
        {message.videos && message.videos.length > 0 && (
          <Videos videos={message.videos} />
        )}
        {message.images && message.images.length > 0 && (
          <Images images={message.images} />
        )}
        {message.audio && message.audio.length > 0 && (
          <Audios audio={message.audio} />
        )}
      </div>
    )
  } else if (message.response_audio) {
    if (!message.response_audio.transcript) {
      messageContent = (
        <div className="mt-2 flex items-start">
          <AgentThinkingLoader />
        </div>
      )
    } else {
      messageContent = (
        <div className="flex w-full flex-col gap-4">
          <MarkdownRenderer>
            {message.response_audio.transcript}
          </MarkdownRenderer>
          {message.response_audio.content && message.response_audio && (
            <Audios audio={[message.response_audio]} />
          )}
        </div>
      )
    }
  } else {
    messageContent = (
      <div className="mt-2">
        <AgentThinkingLoader />
      </div>
    )
  }

  return (
    <div className="font-geist flex flex-row items-start gap-4">
      <div className="flex-shrink-0">
        <Icon type="agent" size="sm" />
      </div>
      {messageContent}
    </div>
  )
}

const UserMessage = memo(({ message }: MessageProps) => {
  return (
    <div className="flex items-start pt-4 text-start max-md:break-words">
      <div className="flex flex-row gap-x-3">
        <p className="text-muted flex items-center gap-x-2 text-sm font-medium">
          <Icon type="user" size="sm" />
        </p>
        <div className="text-md font-geist text-secondary rounded-lg py-1">
          {message.content}
        </div>
      </div>
    </div>
  )
})

AgentMessage.displayName = 'AgentMessage'
UserMessage.displayName = 'UserMessage'
export { AgentMessage, UserMessage }
