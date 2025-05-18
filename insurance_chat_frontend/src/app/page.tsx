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
  '보험 가입 후 1년 이상 경과되었고 특이사항 및 특약사항이 없는 일반적인 경우에, 농협생명보험의 모든 암보험 상품들의 각각 일반암 진단금액은 얼마인가요? 또한 평균 일반암 진단금액은 얼마이며, 가장 높은 진단금과 낮은 진단금은 각각 얼마인가요? 모든 금액은 정확한 수치로 만원 단위로 답변해주세요.',
  '농협생명보험에서 표적항암치료 또는 면역항암치료는 일반적인 암보험 기본계약에서 보장되나요? 아니면 별도 특약에 가입해야 보장받을 수 있나요? 표적항암치료 또는 면역항암치료에 대한 보장 금액 한도와 보장 금액을 수령하기 위한 조건은 각각 어떻게 되나요? 보장 금액 한도는 만원 단위의 정확한 수치로 답변해주세요.',
  '농협생명보험 암보험 상품 중 별도 특약이 없는 경우 진단금을 청구할 때 모든 보험상품에서 공통적으로 요구되는 서류는 무엇인지 모두 나열해주세요. 또한 각 상품별로 요구되는 서류가 다른 경우 각 상품별로 다르게 요구되는 서류를 각 상품별로 모두 나열해주세요.',
  '농협생명보험에서 동일한 사람 명의로 여러 개의 암보험에 가입한 경우, 암 진단금, 수술비, 입원비를 각 보험사에서 중복으로 개별 보장금액을 모두 합산한 전액을 수령할 수 있나요? 아니면 일부만 지급되거나 비례보상 원칙이 적용되어 보상금이 조정되나요? 진단금, 수술비, 입원비 3가지에 대해 각각 설명해주세요.',
  "농협생명보험에서 건강검진 없이 몇 가지 질문만으로 가입 가능한 '간편 심사'가 있는 암보험을 모두 나열해주세요.",
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
          아래 추천 질문을 클릭하여 질문해보세요.
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
