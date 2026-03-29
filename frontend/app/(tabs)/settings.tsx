import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  TextInput,
  Modal,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import { Colors, Spacing, FontSizes, BorderRadius } from '../../constants/theme';
import { useAuth } from '../../contexts/AuthContext';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function SettingsScreen() {
  const router = useRouter();
  const { logout, token } = useAuth();
  const [feedbackModal, setFeedbackModal] = useState(false);
  const [feedbackType, setFeedbackType] = useState('feedback');
  const [feedbackMessage, setFeedbackMessage] = useState('');
  const [contactPreference, setContactPreference] = useState('email');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmitFeedback = async () => {
    if (!feedbackMessage.trim()) {
      Alert.alert('Error', 'Please enter your feedback');
      return;
    }

    setIsSubmitting(true);
    try {
      await axios.post(
        `${BACKEND_URL}/api/feedback`,
        {
          type: feedbackType,
          message: feedbackMessage,
          contact_preference: contactPreference,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      Alert.alert(
        'Thank You!',
        'Your feedback has been received. We will get back to you soon via ' + contactPreference + '.',
        [
          {
            text: 'OK',
            onPress: () => {
              setFeedbackModal(false);
              setFeedbackMessage('');
            },
          },
        ]
      );
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to submit feedback');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            await logout();
            router.replace('/');
          },
        },
      ]
    );
  };

  const SettingItem = ({
    icon,
    title,
    subtitle,
    onPress,
    showChevron = true,
    danger = false,
  }: {
    icon: keyof typeof Ionicons.glyphMap;
    title: string;
    subtitle?: string;
    onPress?: () => void;
    showChevron?: boolean;
    danger?: boolean;
  }) => (
    <TouchableOpacity
      style={styles.settingItem}
      onPress={onPress}
      disabled={!onPress}
    >
      <View style={styles.settingIcon}>
        <Ionicons
          name={icon}
          size={24}
          color={danger ? Colors.error : Colors.sacred}
        />
      </View>
      <View style={styles.settingContent}>
        <Text style={[styles.settingTitle, danger && styles.dangerText]}>
          {title}
        </Text>
        {subtitle && <Text style={styles.settingSubtitle}>{subtitle}</Text>}
      </View>
      {showChevron && (
        <Ionicons name="chevron-forward" size={20} color={Colors.textMuted} />
      )}
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Settings</Text>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* App Information */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>App Information</Text>
          <View style={styles.sectionContent}>
            <SettingItem
              icon="information-circle-outline"
              title="About GitaPath"
              subtitle="Learn more about our mission"
              onPress={() => Alert.alert(
                'About GitaPath',
                'GitaPath is your spiritual companion, bringing the timeless wisdom of the Bhagavad Gita to modern life through AI-powered guidance.'
              )}
            />
            <SettingItem
              icon="book-outline"
              title="Version"
              subtitle="1.0.0"
              showChevron={false}
            />
          </View>
        </View>

        {/* Voice Settings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Voice Settings</Text>
          <View style={styles.sectionContent}>
            <SettingItem
              icon="mic-outline"
              title="Voice Input"
              subtitle="Currently in beta"
              showChevron={false}
            />
            <SettingItem
              icon="volume-high-outline"
              title="Voice Output"
              subtitle="Text-to-speech enabled"
              showChevron={false}
            />
          </View>
        </View>

        {/* Privacy & Security */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Privacy & Security</Text>
          <View style={styles.sectionContent}>
            <SettingItem
              icon="shield-checkmark-outline"
              title="Privacy Policy"
              onPress={() => Alert.alert(
                'Privacy Policy',
                'Your conversations are private and secure. We use encryption to protect your data.'
              )}
            />
            <SettingItem
              icon="document-text-outline"
              title="Terms of Service"
              onPress={() => Alert.alert(
                'Terms of Service',
                'By using GitaPath, you agree to our terms and conditions.'
              )}
            />
          </View>
        </View>

        {/* Support */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Support</Text>
          <View style={styles.sectionContent}>
            <SettingItem
              icon="bug-outline"
              title="Report an Issue"
              subtitle="Something not working?"
              onPress={() => {
                setFeedbackType('issue');
                setFeedbackModal(true);
              }}
            />
            <SettingItem
              icon="chatbox-ellipses-outline"
              title="Give Feedback"
              subtitle="Help us improve GitaPath"
              onPress={() => {
                setFeedbackType('feedback');
                setFeedbackModal(true);
              }}
            />
            <SettingItem
              icon="help-circle-outline"
              title="Help & FAQ"
              onPress={() => Alert.alert(
                'Help',
                'For assistance, please visit our website or contact support.'
              )}
            />
          </View>
        </View>

        {/* Account Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Account</Text>
          <View style={styles.sectionContent}>
            <SettingItem
              icon="log-out-outline"
              title="Logout"
              onPress={handleLogout}
              danger
            />
          </View>
        </View>

        {/* Quote */}
        <View style={styles.quoteCard}>
          <Ionicons name="flower-outline" size={24} color={Colors.sacred} />
          <Text style={styles.quoteText}>
            "Perform your duty with a balanced mind."
          </Text>
          <Text style={styles.quoteReference}>— Bhagavad Gita 2.48</Text>
        </View>
      </ScrollView>

      {/* Feedback Modal */}
      <Modal
        visible={feedbackModal}
        transparent
        animationType="slide"
        onRequestClose={() => setFeedbackModal(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>
                {feedbackType === 'issue' ? 'Report an Issue' : 'Give Feedback'}
              </Text>
              <TouchableOpacity onPress={() => setFeedbackModal(false)}>
                <Ionicons name="close" size={24} color={Colors.text} />
              </TouchableOpacity>
            </View>

            <Text style={styles.modalSubtitle}>
              {feedbackType === 'issue' 
                ? 'Let us know what went wrong' 
                : 'Help us make GitaPath better'}
            </Text>

            <TextInput
              style={styles.feedbackInput}
              placeholder="Type your message here..."
              placeholderTextColor={Colors.textMuted}
              value={feedbackMessage}
              onChangeText={setFeedbackMessage}
              multiline
              numberOfLines={6}
              textAlignVertical="top"
            />

            <Text style={styles.contactLabel}>How should we reach you?</Text>
            <View style={styles.contactOptions}>
              <TouchableOpacity
                style={[
                  styles.contactOption,
                  contactPreference === 'email' && styles.contactOptionActive
                ]}
                onPress={() => setContactPreference('email')}
              >
                <Ionicons 
                  name="mail" 
                  size={20} 
                  color={contactPreference === 'email' ? Colors.sacred : Colors.textMuted} 
                />
                <Text style={[
                  styles.contactOptionText,
                  contactPreference === 'email' && styles.contactOptionTextActive
                ]}>
                  Email
                </Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[
                  styles.contactOption,
                  contactPreference === 'whatsapp' && styles.contactOptionActive
                ]}
                onPress={() => setContactPreference('whatsapp')}
              >
                <Ionicons 
                  name="logo-whatsapp" 
                  size={20} 
                  color={contactPreference === 'whatsapp' ? Colors.sacred : Colors.textMuted} 
                />
                <Text style={[
                  styles.contactOptionText,
                  contactPreference === 'whatsapp' && styles.contactOptionTextActive
                ]}>
                  WhatsApp
                </Text>
              </TouchableOpacity>
            </View>

            <TouchableOpacity
              style={[styles.submitButton, isSubmitting && styles.submitButtonDisabled]}
              onPress={handleSubmitFeedback}
              disabled={isSubmitting}
            >
              <Text style={styles.submitButtonText}>
                {isSubmitting ? 'Submitting...' : 'Submit'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
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
  content: {
    padding: Spacing.md,
  },
  section: {
    marginBottom: Spacing.lg,
  },
  sectionTitle: {
    fontSize: FontSizes.sm,
    fontWeight: 'bold',
    color: Colors.textMuted,
    textTransform: 'uppercase',
    marginBottom: Spacing.sm,
    paddingHorizontal: Spacing.sm,
  },
  sectionContent: {
    backgroundColor: Colors.darkGray,
    borderRadius: BorderRadius.md,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: Colors.border,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  settingIcon: {
    marginRight: Spacing.md,
  },
  settingContent: {
    flex: 1,
  },
  settingTitle: {
    fontSize: FontSizes.md,
    color: Colors.text,
    fontWeight: '600',
  },
  settingSubtitle: {
    fontSize: FontSizes.sm,
    color: Colors.textMuted,
    marginTop: Spacing.xs,
  },
  dangerText: {
    color: Colors.error,
  },
  quoteCard: {
    backgroundColor: Colors.darkGray,
    borderRadius: BorderRadius.md,
    padding: Spacing.lg,
    marginTop: Spacing.lg,
    borderLeftWidth: 4,
    borderLeftColor: Colors.sacred,
    alignItems: 'center',
  },
  quoteText: {
    fontSize: FontSizes.md,
    color: Colors.text,
    textAlign: 'center',
    fontStyle: 'italic',
    marginTop: Spacing.sm,
  },
  quoteReference: {
    fontSize: FontSizes.xs,
    color: Colors.textMuted,
    marginTop: Spacing.sm,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: Colors.darkGray,
    borderTopLeftRadius: BorderRadius.xl,
    borderTopRightRadius: BorderRadius.xl,
    padding: Spacing.lg,
    minHeight: 500,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  modalTitle: {
    fontSize: FontSizes.xl,
    fontWeight: 'bold',
    color: Colors.sacred,
  },
  modalSubtitle: {
    fontSize: FontSizes.sm,
    color: Colors.textSecondary,
    marginBottom: Spacing.lg,
  },
  feedbackInput: {
    backgroundColor: Colors.inputBackground,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    color: Colors.text,
    fontSize: FontSizes.md,
    minHeight: 150,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.lg,
  },
  contactLabel: {
    fontSize: FontSizes.sm,
    color: Colors.textSecondary,
    marginBottom: Spacing.sm,
  },
  contactOptions: {
    flexDirection: 'row',
    gap: Spacing.md,
    marginBottom: Spacing.lg,
  },
  contactOption: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: Spacing.md,
    backgroundColor: Colors.mediumDark,
    borderRadius: BorderRadius.md,
    borderWidth: 2,
    borderColor: Colors.border,
    gap: Spacing.sm,
  },
  contactOptionActive: {
    borderColor: Colors.sacred,
    backgroundColor: Colors.sacred + '20',
  },
  contactOptionText: {
    fontSize: FontSizes.md,
    color: Colors.textMuted,
    fontWeight: '600',
  },
  contactOptionTextActive: {
    color: Colors.sacred,
  },
  submitButton: {
    backgroundColor: Colors.sacred,
    paddingVertical: Spacing.md,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: Colors.dark,
    fontSize: FontSizes.lg,
    fontWeight: 'bold',
  },
});
