import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  Modal,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import * as Clipboard from 'expo-clipboard';
import axios from 'axios';
import { Colors, Spacing, FontSizes, BorderRadius } from '../constants/theme';
import { useAuth } from '../contexts/AuthContext';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

const plans = [
  {
    id: 'basic',
    name: 'Basic',
    price: 500,
    color: '#6B7280',
    icon: 'flower-outline',
    features: [
      'Access to Arjun (Enhanced)',
      'Limited premium responses',
      'Basic chat history',
      'Email support',
    ],
  },
  {
    id: 'warrior',
    name: 'Warrior',
    price: 1000,
    color: '#EF4444',
    icon: 'shield',
    features: [
      'Access to Arjun + Bhima',
      'Faster responses',
      'Unlimited chat history',
      'Priority support',
    ],
  },
  {
    id: 'strategist',
    name: 'Strategist',
    price: 2500,
    color: '#3B82F6',
    icon: 'bulb',
    features: [
      'Krishna + Karna + Yudhishthira',
      'Deep guidance mode',
      'Advanced analytics',
      'VIP support',
    ],
  },
  {
    id: 'divine',
    name: 'Divine',
    price: 5000,
    color: Colors.sacred,
    icon: 'star',
    popular: true,
    features: [
      'All 7 characters unlocked',
      'Priority AI responses',
      'Future features access',
      'Dedicated support',
      'Exclusive insights',
    ],
  },
];

export default function PremiumScreen() {
  const router = useRouter();
  const { token } = useAuth();
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [paymentModal, setPaymentModal] = useState(false);
  const [transactionId, setTransactionId] = useState('');
  const [autoRenew, setAutoRenew] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const UPI_ID = 'cyber.s.sarkar0708@ybl';

  const handleSelectPlan = (plan) => {
    setSelectedPlan(plan);
    setPaymentModal(true);
  };

  const copyUPI = async () => {
    await Clipboard.setStringAsync(UPI_ID);
    Alert.alert('Copied!', 'UPI ID copied to clipboard');
  };

  const handleVerifyPayment = async () => {
    if (!transactionId.trim()) {
      Alert.alert('Error', 'Please enter transaction ID');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await axios.post(
        `${BACKEND_URL}/api/premium/verify-payment`,
        {
          plan: selectedPlan.name,
          amount: selectedPlan.price,
          transaction_id: transactionId,
          auto_renew: autoRenew,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.status === 200) {
        setPaymentModal(false);
        setTransactionId('');
        Alert.alert(
          'Payment Submitted!',
          'Thank you! Your payment is being verified. You will receive access within 24 hours.',
          [
            {
              text: 'OK',
              onPress: () => router.back(),
            },
          ]
        );
      }
    } catch (error) {
      console.error('Payment verification error:', error);
      Alert.alert('Error', error.response?.data?.detail || 'Failed to submit payment');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={Colors.sacred} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Upgrade to Premium</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Title Section */}
        <View style={styles.titleSection}>
          <Text style={styles.mainTitle}>Unlock Divine Guidance</Text>
          <Text style={styles.subtitle}>
            Access powerful AI personalities from the Mahabharata
          </Text>
        </View>

        {/* Plans */}
        {plans.map((plan) => (
          <TouchableOpacity
            key={plan.id}
            style={[
              styles.planCard,
              plan.popular && styles.popularCard,
            ]}
            onPress={() => handleSelectPlan(plan)}
          >
            {plan.popular && (
              <View style={styles.popularBadge}>
                <Text style={styles.popularText}>MOST POPULAR</Text>
              </View>
            )}

            <View style={styles.planHeader}>
              <View style={[styles.planIcon, { backgroundColor: plan.color + '20' }]}>
                <Ionicons name={plan.icon} size={32} color={plan.color} />
              </View>
              <View style={styles.planTitleSection}>
                <Text style={[styles.planName, { color: plan.color }]}>{plan.name}</Text>
                <Text style={styles.planPrice}>
                  ₹{plan.price}<Text style={styles.priceUnit}>/month</Text>
                </Text>
              </View>
            </View>

            <View style={styles.featuresList}>
              {plan.features.map((feature, index) => (
                <View key={index} style={styles.featureItem}>
                  <Ionicons name="checkmark-circle" size={20} color={plan.color} />
                  <Text style={styles.featureText}>{feature}</Text>
                </View>
              ))}
            </View>

            <TouchableOpacity
              style={[styles.selectButton, { backgroundColor: plan.color }]}
              onPress={() => handleSelectPlan(plan)}
            >
              <Text style={styles.selectButtonText}>Choose {plan.name}</Text>
            </TouchableOpacity>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Payment Modal */}
      <Modal
        visible={paymentModal}
        animationType="slide"
        transparent
        onRequestClose={() => setPaymentModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>
                {selectedPlan?.name} Plan
              </Text>
              <TouchableOpacity onPress={() => setPaymentModal(false)}>
                <Ionicons name="close" size={28} color={Colors.text} />
              </TouchableOpacity>
            </View>

            <ScrollView>
              <Text style={styles.modalAmount}>₹{selectedPlan?.price}/month</Text>

              {/* UPI Section */}
              <View style={styles.upiSection}>
                <Text style={styles.upiLabel}>Pay via UPI</Text>
                <Text style={styles.upiId}>{UPI_ID}</Text>
                <TouchableOpacity style={styles.copyButton} onPress={copyUPI}>
                  <Ionicons name="copy-outline" size={16} color={Colors.dark} />
                  <Text style={styles.copyButtonText}>Copy UPI ID</Text>
                </TouchableOpacity>
              </View>

              {/* QR Placeholder */}
              <View style={styles.qrPlaceholder}>
                <Ionicons name="qr-code" size={80} color={Colors.textMuted} />
                <Text style={styles.qrText}>Scan QR to Pay</Text>
              </View>

              {/* Auto Renew */}
              <View style={styles.autoRenewSection}>
                <View>
                  <Text style={styles.autoRenewLabel}>Enable Auto-Renew</Text>
                  <Text style={styles.autoRenewNote}>
                    Subscription renews automatically
                  </Text>
                </View>
                <TouchableOpacity
                  style={[styles.toggle, autoRenew && styles.toggleActive]}
                  onPress={() => setAutoRenew(!autoRenew)}
                >
                  <View
                    style={[
                      styles.toggleThumb,
                      autoRenew && styles.toggleThumbActive,
                    ]}
                  />
                </TouchableOpacity>
              </View>

              {/* Transaction ID */}
              <View style={styles.inputSection}>
                <Text style={styles.inputLabel}>Transaction ID *</Text>
                <TextInput
                  style={styles.input}
                  placeholder="Enter UPI transaction ID"
                  placeholderTextColor={Colors.textMuted}
                  value={transactionId}
                  onChangeText={setTransactionId}
                />
              </View>

              {/* Verify Button */}
              <TouchableOpacity
                style={[
                  styles.verifyButton,
                  isSubmitting && styles.verifyButtonDisabled,
                ]}
                onPress={handleVerifyPayment}
                disabled={isSubmitting}
              >
                <Text style={styles.verifyButtonText}>
                  {isSubmitting ? 'Verifying...' : 'Verify Payment'}
                </Text>
              </TouchableOpacity>

              {/* Note */}
              <View style={styles.noteBox}>
                <Ionicons name="information-circle" size={20} color={Colors.sacred} />
                <Text style={styles.noteText}>
                  Your payment will be verified within 24 hours. Access will be unlocked
                  after verification.
                </Text>
              </View>
            </ScrollView>
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
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: Spacing.md,
    backgroundColor: Colors.darkGray,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  backButton: {
    padding: Spacing.xs,
  },
  headerTitle: {
    fontSize: FontSizes.xl,
    fontWeight: 'bold',
    color: Colors.sacred,
  },
  content: {
    padding: Spacing.lg,
  },
  titleSection: {
    alignItems: 'center',
    marginBottom: Spacing.xl,
  },
  mainTitle: {
    fontSize: FontSizes.xxl,
    fontWeight: 'bold',
    color: Colors.sacred,
    textAlign: 'center',
    marginBottom: Spacing.sm,
  },
  subtitle: {
    fontSize: FontSizes.md,
    color: Colors.textSecondary,
    textAlign: 'center',
  },
  planCard: {
    backgroundColor: Colors.darkGray,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    marginBottom: Spacing.lg,
    borderWidth: 2,
    borderColor: Colors.border,
  },
  popularCard: {
    borderColor: Colors.sacred,
    backgroundColor: Colors.sacred + '10',
  },
  popularBadge: {
    position: 'absolute',
    top: Spacing.md,
    right: Spacing.md,
    backgroundColor: Colors.sacred,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.full,
  },
  popularText: {
    color: Colors.dark,
    fontSize: FontSizes.xs,
    fontWeight: 'bold',
  },
  planHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.lg,
  },
  planIcon: {
    width: 60,
    height: 60,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.md,
  },
  planTitleSection: {
    flex: 1,
  },
  planName: {
    fontSize: FontSizes.xl,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  planPrice: {
    fontSize: FontSizes.xxl,
    fontWeight: 'bold',
    color: Colors.text,
  },
  priceUnit: {
    fontSize: FontSizes.sm,
    color: Colors.textSecondary,
  },
  featuresList: {
    marginBottom: Spacing.lg,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.sm,
    gap: Spacing.sm,
  },
  featureText: {
    flex: 1,
    fontSize: FontSizes.sm,
    color: Colors.textSecondary,
  },
  selectButton: {
    paddingVertical: Spacing.md,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
  },
  selectButtonText: {
    color: Colors.dark,
    fontSize: FontSizes.md,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.9)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: Colors.darkGray,
    borderTopLeftRadius: BorderRadius.xl,
    borderTopRightRadius: BorderRadius.xl,
    padding: Spacing.lg,
    maxHeight: '90%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.lg,
  },
  modalTitle: {
    fontSize: FontSizes.xl,
    fontWeight: 'bold',
    color: Colors.sacred,
  },
  modalAmount: {
    fontSize: FontSizes.xxxl,
    fontWeight: 'bold',
    color: Colors.text,
    textAlign: 'center',
    marginBottom: Spacing.xl,
  },
  upiSection: {
    backgroundColor: Colors.sacred + '20',
    borderWidth: 1,
    borderColor: Colors.sacred,
    borderRadius: BorderRadius.md,
    padding: Spacing.lg,
    marginBottom: Spacing.lg,
  },
  upiLabel: {
    fontSize: FontSizes.sm,
    color: Colors.textSecondary,
    marginBottom: Spacing.xs,
    textTransform: 'uppercase',
  },
  upiId: {
    fontSize: FontSizes.lg,
    fontWeight: 'bold',
    color: Colors.sacred,
    marginBottom: Spacing.md,
  },
  copyButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.sacred,
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.md,
    borderRadius: BorderRadius.md,
    alignSelf: 'flex-start',
    gap: Spacing.xs,
  },
  copyButtonText: {
    color: Colors.dark,
    fontWeight: 'bold',
  },
  qrPlaceholder: {
    backgroundColor: Colors.mediumDark,
    height: 200,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.lg,
  },
  qrText: {
    color: Colors.textMuted,
    marginTop: Spacing.sm,
  },
  autoRenewSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: Colors.mediumDark,
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    marginBottom: Spacing.lg,
  },
  autoRenewLabel: {
    fontSize: FontSizes.md,
    color: Colors.text,
    fontWeight: '600',
  },
  autoRenewNote: {
    fontSize: FontSizes.xs,
    color: Colors.textMuted,
  },
  toggle: {
    width: 50,
    height: 28,
    backgroundColor: Colors.inputBackground,
    borderRadius: 14,
    padding: 2,
  },
  toggleActive: {
    backgroundColor: Colors.sacred,
  },
  toggleThumb: {
    width: 24,
    height: 24,
    backgroundColor: Colors.text,
    borderRadius: 12,
  },
  toggleThumbActive: {
    transform: [{ translateX: 22 }],
  },
  inputSection: {
    marginBottom: Spacing.lg,
  },
  inputLabel: {
    fontSize: FontSizes.sm,
    color: Colors.textSecondary,
    marginBottom: Spacing.sm,
    textTransform: 'uppercase',
  },
  input: {
    backgroundColor: Colors.inputBackground,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    color: Colors.text,
    fontSize: FontSizes.md,
  },
  verifyButton: {
    backgroundColor: Colors.sacred,
    paddingVertical: Spacing.md,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
    marginBottom: Spacing.lg,
  },
  verifyButtonDisabled: {
    opacity: 0.6,
  },
  verifyButtonText: {
    color: Colors.dark,
    fontSize: FontSizes.lg,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  noteBox: {
    flexDirection: 'row',
    backgroundColor: Colors.sacred + '20',
    borderLeftWidth: 3,
    borderLeftColor: Colors.sacred,
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    gap: Spacing.sm,
  },
  noteText: {
    flex: 1,
    fontSize: FontSizes.sm,
    color: Colors.textSecondary,
  },
});
