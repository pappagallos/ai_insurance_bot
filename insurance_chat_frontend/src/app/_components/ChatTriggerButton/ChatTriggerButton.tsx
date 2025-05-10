import styles from './ChatTriggerButton.module.scss';

interface ChatTriggerButtonProps {
  onClick: VoidFunction;
}

export default function ChatTriggerButton({ onClick }: ChatTriggerButtonProps) {
  return (
    <div className={styles.chat_trigger} onClick={onClick}>
      <img
        src="/assets/app_main_image.png"
        alt="chat_trigger"
        className={styles.chat_trigger_icon}
      />
    </div>
  );
}
