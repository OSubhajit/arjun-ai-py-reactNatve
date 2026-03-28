import React, { useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../contexts/AuthContext';
import { Colors, Spacing, FontSizes, BorderRadius } from '../constants/theme';
import { Ionicons } from '@expo/vector-icons';

export default function WelcomeScreen() {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && user) {
      router.replace('/(tabs)/chat');
    }
  }, [user, isLoading]);

  if (isLoading) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Sacred Symbol */}
      <View style={styles.symbolContainer}>
        <Ionicons name="flower-outline" size={80} color={Colors.sacred} />
      </View>

      {/* App Name */}
      <Text style={styles.appName}>GitaPath</Text>
      <Text style={styles.tagline}>Wisdom of the Bhagavad Gita</Text>

      {/* Sanskrit Quote */}
      <View style={styles.quoteContainer}>
        <Text style={styles.sanskritQuote}>कर्मण्येवाधिकारस्ते मा फलेषु कदाचन</Text>
        <Text style={styles.englishQuote}>
          "You have the right to perform your actions,{' \n'}
          but you are not entitled to the fruits of the actions."
        </Text>
        <Text style={styles.reference}>— Bhagavad Gita 2.47</Text>
      </View>

      {/* Buttons */}
      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={styles.primaryButton}
          onPress={() => router.push('/(auth)/login')}
        >
          <Text style={styles.primaryButtonText}>Enter the Path</Text>
          <Ionicons name="arrow-forward" size={20} color={Colors.dark} />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.secondaryButton}
          onPress={() => router.push('/(auth)/register')}
        >
          <Text style={styles.secondaryButtonText}>Begin My Journey</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.dark,
    alignItems: 'center',
    justifyContent: 'center',
    padding: Spacing.lg,
  },
  symbolContainer: {
    marginBottom: Spacing.xl,
  },
  appName: {
    fontSize: FontSizes.xxxl,
    fontWeight: 'bold',
    color: Colors.sacred,
    marginBottom: Spacing.sm,
  },
  tagline: {
    fontSize: FontSizes.md,
    color: Colors.textSecondary,
    marginBottom: Spacing.xxl,
  },
  quoteContainer: {
    backgroundColor: Colors.darkGray,
    padding: Spacing.lg,
    borderRadius: BorderRadius.md,
    borderLeftWidth: 4,
    borderLeftColor: Colors.sacred,
    marginBottom: Spacing.xxl,
  },
  sanskritQuote: {
    fontSize: FontSizes.md,
    color: Colors.sacredLight,
    textAlign: 'center',
    marginBottom: Spacing.md,
    fontWeight: '600',
  },
  englishQuote: {
    fontSize: FontSizes.sm,
    color: Colors.textSecondary,
    textAlign: 'center',
    marginBottom: Spacing.sm,
    fontStyle: 'italic',
    lineHeight: 20,
  },
  reference: {
    fontSize: FontSizes.xs,
    color: Colors.textMuted,
    textAlign: 'center',
  },
  buttonContainer: {
    width: '100%',
    gap: Spacing.md,
  },
  primaryButton: {
    backgroundColor: Colors.sacred,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.lg,
    borderRadius: BorderRadius.md,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: Spacing.sm,
  },
  primaryButtonText: {
    color: Colors.dark,
    fontSize: FontSizes.lg,
    fontWeight: 'bold',
  },
  secondaryButton: {
    backgroundColor: 'transparent',
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.lg,
    borderRadius: BorderRadius.md,
    borderWidth: 2,
    borderColor: Colors.sacred,
  },
  secondaryButtonText: {
    color: Colors.sacred,
    fontSize: FontSizes.lg,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  loadingText: {
    color: Colors.text,
    fontSize: FontSizes.lg,
  },
});
