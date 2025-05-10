'use client';

import React, { useContext } from 'react';

// Components
import ChatIcon from '@mui/icons-material/Chat';
import Chat from './_components/Chat/Chat';
import ChatTriggerButton from './_components/ChatTriggerButton/ChatTriggerButton';
import {
  ChatEnvironmentContext,
  ChatEnvironmentProvider,
  InitChatEnvironmentContextType,
} from './_components/Chat/ChatEnvironmentContext';

import styles from './Page.module.scss';
import { InfoOutlineSharp } from '@mui/icons-material';

const context: InitChatEnvironmentContextType = {
  isOpen: false,
  appName: process.env.NEXT_PUBLIC_APP_NAME as string,
  appDescription: process.env.NEXT_PUBLIC_APP_DESCRIPTION as string,
  appIcon: process.env.NEXT_PUBLIC_APP_ICON as string,
  appMainImage: process.env.NEXT_PUBLIC_APP_MAIN_IMAGE as string,
  appBackground: process.env.NEXT_PUBLIC_APP_BACKGROUND_IMAGE as string,
  messageEditorPlaceholder: process.env.NEXT_PUBLIC_MESSAGE_EDITOR_PLACEHOLDER as string,
  botName: process.env.NEXT_PUBLIC_BOT_NAME as string,
  botAvatar: process.env.NEXT_PUBLIC_BOT_AVATAR as string,
  botWelcomeMessage: process.env.NEXT_PUBLIC_BOT_WELCOME_MESSAGE as string,
  disabledSendButton: true,
  sendMessage: () => {},
};

const recommendQuestions = [
  '병원에 머무는 최소 시간, 입원 인정 장소 등의 약관에서 정의하는 입원의 기준은 어떤가요? 상품마다 큰 차이가 있나요?',
  '알고 있는 암보험 상품들의 일반암 진단금액은 평균적으로 얼마 정도이며, 상품 간 차이는 큰 편인가요? 가장 높은 진단금과 낮은 진단금은 각각 얼마 수준인가요?',
  '보험료 납입 면제 조건에 대해 약관에서 어떻게 설명하고 있는지, 관련 조항들을 찾아서 보여주세요.',
  '건강검진 없이 간편 심사만으로 가입할 수 있는 암보험 상품들이 많나요? 이런 상품은 일반 상품과 비교했을 때 보험료나 보장 내용에 어떤 차이가 있는 경향이 있나요?',
  '여러 개의 암보험에 가입했을 경우, 진단금이나 수술비, 입원비를 각각의 보험에서 모두 받을 수 있나요? 아니면 일부만 지급(비례보상 등)하는 경우도 있나요? 약관의 일반적인 규정은 어떤가요?',
];

export default function Page() {
  return (
    <ChatEnvironmentProvider {...context}>
      <div className={styles.about_chat}>
        <h1 className={styles.about_chat_title}>농협생명보험 AI 보험 상담사</h1>
        <h2 className={styles.about_chat_subtitle}>전문 보험 상담사 코리가 친절하게 답변합니다</h2>
        <p className={styles.about_chat_description}>
          지금 농협생명보험의 5가지 암보험 상품에 대해 모두 질문해 보시거나,
          <br />
          궁금한 점을 코리에게 직접 물어보거나 아래 추천 질문을 클릭해보세요.
        </p>
        <RecommendQuestions />
        <p className={styles.about_chat_author}>
          <InfoOutlineSharp className={styles.about_chat_author_icon} />
          멘토 한상준 | 패스트캠퍼스 AI 엔지니어 1차 프로젝트 2팀
        </p>
      </div>
      <ChatComponent />
    </ChatEnvironmentProvider>
  );
}

export const RecommendQuestions = () => {
  const chatEnvironmentContext = useContext(ChatEnvironmentContext);

  return (
    <div className={styles.recommend_questions}>
      <div className={styles.recommend_questions_title}>
        <ChatIcon className={styles.chat_icon} />
        <span>추천 질문</span>
      </div>
      <ul className={styles.recommend_questions_list}>
        {recommendQuestions.map((question, index) => (
          <li key={index} onClick={() => chatEnvironmentContext?.sendMessage(question)}>
            <span>{question}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export const ChatComponent = () => {
  const chatEnvironmentContext = useContext(ChatEnvironmentContext);

  return (
    <Chat
      chatTrigger={
        <ChatTriggerButton
          onClick={() => chatEnvironmentContext?.setIsOpen(!chatEnvironmentContext?.isOpen)}
        />
      }
    />
  );
};
