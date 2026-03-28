import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, Spacing, FontSizes, BorderRadius } from '../../constants/theme';
import { useAuth } from '../../contexts/AuthContext';

export default function SettingsScreen() {
  const router = useRouter();
  const { logout } = useAuth();

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
              icon="help-circle-outline"
              title="Help & FAQ"
              onPress={() => Alert.alert(
                'Help',
                'For assistance, please visit our website or contact support.'
              )}
            />
            <SettingItem
              icon="chatbox-ellipses-outline"
              title="Contact Us"
              subtitle="Get in touch with our team"
              onPress={() => Alert.alert(
                'Contact Us',
                'Email: support@gitapath.com'
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
});
