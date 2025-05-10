import cn from 'classnames';
import React, { useContext } from 'react';

import styles from './ChatTriggerButton.module.scss';
import { ChatOutlined } from '@mui/icons-material';
import { ChatEnvironmentContext } from '../Chat/ChatEnvironmentContext';

interface ChatTriggerButtonProps {
  onClick: VoidFunction;
}

const ChatTriggerFloatingButton = ({ onClick }: ChatTriggerButtonProps) => {
  return (
    <div className={styles.chat_trigger} onClick={onClick}>
      <img
        src="/assets/app_main_image.png"
        alt="chat_trigger"
        className={styles.chat_trigger_icon}
      />
    </div>
  );
};

const ChatTriggerMessage = () => {
  const chatEnvironmentContext = useContext(ChatEnvironmentContext);

  return (
    <React.Fragment>
      <div
        className={cn(styles.chat_trigger_message, {
          [styles.hidden]: chatEnvironmentContext?.isOpen,
        })}
        onClick={() => chatEnvironmentContext?.setIsOpen(true)}
      >
        <p className={styles.title}>보험에 관련된 궁금한 점을 물어보세요</p>
        <p className={styles.description}>
          <ChatOutlined className={styles.chat_trigger_message_icon} />
          보험 상담사 코리와 대화 시작하기
        </p>
      </div>
    </React.Fragment>
  );
};

export default function ChatTriggerButton({ onClick }: ChatTriggerButtonProps) {
  return (
    <React.Fragment>
      <ChatTriggerMessage />
      <ChatTriggerFloatingButton onClick={onClick} />
    </React.Fragment>
  );
}
