import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import { format } from 'date-fns';
import { Colors, Spacing, FontSizes, BorderRadius } from '../../constants/theme';
import { useAuth } from '../../contexts/AuthContext';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface ChatHistory {
  id: string;
  message: string;
  response: string;
  timestamp: string;
}

export default function HistoryScreen() {
  const { token } = useAuth();
  const [history, setHistory] = useState<ChatHistory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/chat/history`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setHistory(response.data);
    } catch (error: any) {
      console.error('Failed to fetch history:', error);
      Alert.alert('Error', 'Failed to load chat history');
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchHistory();
  };

  const deleteChat = async (chatId: string) => {
    Alert.alert(
      'Delete Chat',
      'Are you sure you want to delete this conversation?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await axios.delete(`${BACKEND_URL}/api/chat/${chatId}`, {
                headers: {
                  Authorization: `Bearer ${token}`,
                },
              });
              setHistory((prev) => prev.filter((item) => item.id !== chatId));
            } catch (error) {
              Alert.alert('Error', 'Failed to delete chat');
            }
          },
        },
      ]
    );
  };

  const renderHistoryItem = ({ item }: { item: ChatHistory }) => {
    const isExpanded = expandedId === item.id;

    return (
      <View style={styles.historyItem}>
        <TouchableOpacity
          style={styles.historyHeader}
          onPress={() => setExpandedId(isExpanded ? null : item.id)}
        >
          <View style={styles.historyInfo}>
            <Ionicons name="chatbubble-outline" size={20} color={Colors.sacred} />
            <View style={styles.historyText}>
              <Text style={styles.historyMessage} numberOfLines={isExpanded ? undefined : 1}>
                {item.message}
              </Text>
              <Text style={styles.historyTime}>
                {format(new Date(item.timestamp), 'MMM dd, yyyy • hh:mm a')}
              </Text>
            </View>
          </View>
          <View style={styles.historyActions}>
            <TouchableOpacity
              style={styles.deleteButton}
              onPress={() => deleteChat(item.id)}
            >
              <Ionicons name="trash-outline" size={20} color={Colors.error} />
            </TouchableOpacity>
            <Ionicons
              name={isExpanded ? 'chevron-up' : 'chevron-down'}
              size={20}
              color={Colors.textMuted}
            />
          </View>
        </TouchableOpacity>

        {isExpanded && (
          <View style={styles.historyResponse}>
            <Text style={styles.responseLabel}>Arjun's Response:</Text>
            <Text style={styles.responseText}>{item.response}</Text>
          </View>
        )}
      </View>
    );
  };

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Chat History</Text>
        </View>
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color={Colors.sacred} />
          <Text style={styles.loadingText}>Loading history...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Chat History</Text>
        <Text style={styles.headerSubtitle}>{history.length} conversations</Text>
      </View>

      {history.length === 0 ? (
        <View style={styles.centerContainer}>
          <Ionicons name="time-outline" size={64} color={Colors.textMuted} />
          <Text style={styles.emptyText}>No chat history yet</Text>
          <Text style={styles.emptySubtext}>Start a conversation with Arjun</Text>
        </View>
      ) : (
        <FlatList
          data={history}
          keyExtractor={(item) => item.id}
          renderItem={renderHistoryItem}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor={Colors.sacred}
            />
          }
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.dark,
  },
  header: {
    padding: Spacing.md,
    backgroundColor: Colors.darkGray,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  headerTitle: {
    fontSize: FontSizes.xl,
    fontWeight: 'bold',
    color: Colors.sacred,
  },
  headerSubtitle: {
    fontSize: FontSizes.sm,
    color: Colors.textSecondary,
    marginTop: Spacing.xs,
  },
  centerContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: Spacing.lg,
  },
  loadingText: {
    color: Colors.textSecondary,
    fontSize: FontSizes.md,
    marginTop: Spacing.md,
  },
  emptyText: {
    fontSize: FontSizes.lg,
    fontWeight: 'bold',
    color: Colors.text,
    marginTop: Spacing.md,
  },
  emptySubtext: {
    fontSize: FontSizes.md,
    color: Colors.textSecondary,
    marginTop: Spacing.xs,
  },
  listContent: {
    padding: Spacing.md,
  },
  historyItem: {
    backgroundColor: Colors.darkGray,
    borderRadius: BorderRadius.md,
    marginBottom: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  historyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: Spacing.md,
  },
  historyInfo: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    flex: 1,
  },
  historyText: {
    flex: 1,
    marginLeft: Spacing.sm,
  },
  historyMessage: {
    fontSize: FontSizes.md,
    color: Colors.text,
    marginBottom: Spacing.xs,
  },
  historyTime: {
    fontSize: FontSizes.xs,
    color: Colors.textMuted,
  },
  historyActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  deleteButton: {
    padding: Spacing.xs,
  },
  historyResponse: {
    padding: Spacing.md,
    paddingTop: 0,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  responseLabel: {
    fontSize: FontSizes.sm,
    color: Colors.sacred,
    fontWeight: 'bold',
    marginBottom: Spacing.xs,
  },
  responseText: {
    fontSize: FontSizes.md,
    color: Colors.textSecondary,
    lineHeight: 22,
  },
});
