import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import * as Speech from 'expo-speech';
import { Audio } from 'expo-av';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Colors, Spacing, FontSizes, BorderRadius } from '../../constants/theme';
import { useAuth } from '../../contexts/AuthContext';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

export default function ChatScreen() {
  const { user, token } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const flatListRef = useRef<FlatList>(null);
  const recordingRef = useRef<Audio.Recording | null>(null);

  useEffect(() => {
    // Welcome message
    setMessages([
      {
        id: '1',
        text: `Namaste ${user?.name || 'Friend'}! 🙏\n\nI am Arjun, your spiritual guide. I'm here to help you navigate life's challenges through the timeless wisdom of the Bhagavad Gita.\n\nHow may I assist you on your journey today?`,
        isUser: false,
        timestamp: new Date(),
      },
    ]);
  }, []);

  const sendMessage = async (messageText: string) => {
    if (!messageText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: messageText.trim(),
      isUser: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await axios.post(
        `${BACKEND_URL}/api/chat/send`,
        { message: messageText.trim() },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const aiMessage: Message = {
        id: response.data.id,
        text: response.data.response,
        isUser: false,
        timestamp: new Date(response.data.timestamp),
      };

      setMessages((prev) => [...prev, aiMessage]);

      // Auto-scroll to bottom
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    } catch (error: any) {
      console.error('Chat error:', error);
      Alert.alert('Error', 'Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const speakMessage = (text: string) => {
    if (isSpeaking) {
      Speech.stop();
      setIsSpeaking(false);
    } else {
      Speech.speak(text, {
        language: 'en-US',
        pitch: 1.0,
        rate: 0.9,
        onStart: () => setIsSpeaking(true),
        onDone: () => setIsSpeaking(false),
        onStopped: () => setIsSpeaking(false),
        onError: () => setIsSpeaking(false),
      });
    }
  };

  const startRecording = async () => {
    try {
      // Request permissions
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Denied', 'Please grant microphone permission to use voice input');
        return;
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const recording = new Audio.Recording();
      await recording.prepareToRecordAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
      await recording.startAsync();
      recordingRef.current = recording;
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
      Alert.alert('Error', 'Failed to start recording');
    }
  };

  const stopRecording = async () => {
    if (!recordingRef.current) return;

    try {
      await recordingRef.current.stopAndUnloadAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
      });
      setIsRecording(false);
      
      // For now, show a message that voice transcription is not implemented
      // In production, you would use a speech-to-text service
      Alert.alert(
        'Voice Input',
        'Voice transcription is not yet implemented. Please type your message.',
        [{ text: 'OK' }]
      );
      
      recordingRef.current = null;
    } catch (error) {
      console.error('Failed to stop recording:', error);
    }
  };

  const renderMessage = ({ item }: { item: Message }) => {
    return (
      <View
        style={[
          styles.messageBubble,
          item.isUser ? styles.userMessage : styles.aiMessage,
        ]}
      >
        <Text style={item.isUser ? styles.userText : styles.aiText}>{item.text}</Text>
        {!item.isUser && (
          <TouchableOpacity
            style={styles.speakButton}
            onPress={() => speakMessage(item.text)}
          >
            <Ionicons
              name={isSpeaking ? 'volume-high' : 'volume-medium-outline'}
              size={20}
              color={Colors.sacred}
            />
          </TouchableOpacity>
        )}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <Ionicons name="flower-outline" size={32} color={Colors.sacred} />
        <Text style={styles.headerTitle}>Arjun AI</Text>
        <View style={styles.headerSubtitle}>
          <View style={styles.onlineIndicator} />
          <Text style={styles.onlineText}>Available</Text>
        </View>
      </View>

      {/* Messages */}
      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={(item) => item.id}
        renderItem={renderMessage}
        contentContainerStyle={styles.messagesList}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
      />

      {/* Loading indicator */}
      {isLoading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="small" color={Colors.sacred} />
          <Text style={styles.loadingText}>Arjun is thinking...</Text>
        </View>
      )}

      {/* Input Area */}
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={90}
      >
        <View style={styles.inputContainer}>
          <TouchableOpacity
            style={[styles.voiceButton, isRecording && styles.voiceButtonActive]}
            onPress={isRecording ? stopRecording : startRecording}
          >
            <Ionicons
              name={isRecording ? 'stop-circle' : 'mic'}
              size={24}
              color={isRecording ? Colors.error : Colors.sacred}
            />
          </TouchableOpacity>

          <TextInput
            style={styles.input}
            placeholder="Ask Arjun for guidance..."
            placeholderTextColor={Colors.textMuted}
            value={inputText}
            onChangeText={setInputText}
            multiline
            maxLength={500}
            editable={!isLoading}
          />

          <TouchableOpacity
            style={[styles.sendButton, (!inputText.trim() || isLoading) && styles.sendButtonDisabled]}
            onPress={() => sendMessage(inputText)}
            disabled={!inputText.trim() || isLoading}
          >
            <Ionicons name="send" size={20} color={Colors.dark} />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.dark,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: Spacing.md,
    backgroundColor: Colors.darkGray,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  headerTitle: {
    fontSize: FontSizes.xl,
    fontWeight: 'bold',
    color: Colors.sacred,
    marginLeft: Spacing.sm,
    flex: 1,
  },
  headerSubtitle: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  onlineIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: Colors.success,
    marginRight: Spacing.xs,
  },
  onlineText: {
    fontSize: FontSizes.xs,
    color: Colors.textSecondary,
  },
  messagesList: {
    padding: Spacing.md,
  },
  messageBubble: {
    maxWidth: '80%',
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    marginBottom: Spacing.md,
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: Colors.sacred,
  },
  aiMessage: {
    alignSelf: 'flex-start',
    backgroundColor: Colors.darkGray,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  userText: {
    color: Colors.dark,
    fontSize: FontSizes.md,
  },
  aiText: {
    color: Colors.text,
    fontSize: FontSizes.md,
    lineHeight: 22,
  },
  speakButton: {
    marginTop: Spacing.sm,
    alignSelf: 'flex-start',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: Spacing.sm,
  },
  loadingText: {
    color: Colors.textSecondary,
    fontSize: FontSizes.sm,
    marginLeft: Spacing.sm,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: Spacing.md,
    backgroundColor: Colors.darkGray,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  voiceButton: {
    padding: Spacing.sm,
    marginRight: Spacing.sm,
  },
  voiceButtonActive: {
    backgroundColor: Colors.mediumDark,
    borderRadius: BorderRadius.full,
  },
  input: {
    flex: 1,
    backgroundColor: Colors.inputBackground,
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    color: Colors.text,
    fontSize: FontSizes.md,
    maxHeight: 100,
  },
  sendButton: {
    backgroundColor: Colors.sacred,
    padding: Spacing.sm,
    borderRadius: BorderRadius.full,
    marginLeft: Spacing.sm,
    width: 44,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendButtonDisabled: {
    opacity: 0.4,
  },
});
