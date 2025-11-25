import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { farmersAPI } from '../api/client';

interface OnboardingFormData {
    farmer_id: string;
    name: string;
    mobile: string;
    consent_given: boolean;
}

interface FarmerOnboardingProps {
    onSuccess: (farmerId: string) => void;
}

const FarmerOnboarding: React.FC<FarmerOnboardingProps> = ({ onSuccess }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const {
        register,
        handleSubmit,
        formState: { errors },
        reset,
    } = useForm<OnboardingFormData>();

    const onSubmit = async (data: OnboardingFormData) => {
        setLoading(true);
        setError(null);

        try {
            await farmersAPI.create(data);
            reset();
            onSuccess(data.farmer_id);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to onboard farmer. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">
                Onboard New Farmer
            </h2>

            {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-800">{error}</p>
                </div>
            )}

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                <div>
                    <label htmlFor="farmer_id" className="block text-sm font-medium text-gray-700 mb-2">
                        Farmer ID *
                    </label>
                    <input
                        id="farmer_id"
                        type="text"
                        placeholder="e.g., FRM000001"
                        className="input-field"
                        {...register('farmer_id', {
                            required: 'Farmer ID is required',
                            pattern: {
                                value: /^FRM\d{6}$/,
                                message: 'Farmer ID must be in format FRM000001',
                            },
                        })}
                    />
                    {errors.farmer_id && (
                        <p className="mt-1 text-sm text-red-600">{errors.farmer_id.message}</p>
                    )}
                </div>

                <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                        Full Name *
                    </label>
                    <input
                        id="name"
                        type="text"
                        placeholder="Enter farmer's full name"
                        className="input-field"
                        {...register('name', {
                            required: 'Name is required',
                            minLength: {
                                value: 3,
                                message: 'Name must be at least 3 characters',
                            },
                        })}
                    />
                    {errors.name && (
                        <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                    )}
                </div>

                <div>
                    <label htmlFor="mobile" className="block text-sm font-medium text-gray-700 mb-2">
                        Mobile Number *
                    </label>
                    <input
                        id="mobile"
                        type="tel"
                        placeholder="+919876543210"
                        className="input-field"
                        {...register('mobile', {
                            required: 'Mobile number is required',
                            pattern: {
                                value: /^\+91\d{10}$/,
                                message: 'Mobile must be in format +919876543210',
                            },
                        })}
                    />
                    {errors.mobile && (
                        <p className="mt-1 text-sm text-red-600">{errors.mobile.message}</p>
                    )}
                </div>

                <div className="flex items-start">
                    <input
                        id="consent_given"
                        type="checkbox"
                        className="mt-1 h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                        {...register('consent_given', {
                            required: 'Consent is required to proceed',
                        })}
                    />
                    <label htmlFor="consent_given" className="ml-3 text-sm text-gray-700">
                        I confirm that the farmer has given consent to access their Agri Stack data
                        for credit scoring purposes. *
                    </label>
                </div>
                {errors.consent_given && (
                    <p className="text-sm text-red-600">{errors.consent_given.message}</p>
                )}

                <div className="pt-4 flex gap-3">
                    <button
                        type="submit"
                        disabled={loading}
                        className="btn-primary flex-1"
                    >
                        {loading ? 'Onboarding...' : 'Onboard Farmer'}
                    </button>
                    <button
                        type="button"
                        onClick={() => reset()}
                        disabled={loading}
                        className="btn-secondary"
                    >
                        Clear
                    </button>
                </div>
            </form>

            <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
                <p className="text-sm text-green-800">
                    <strong>ℹ️ Note:</strong> After onboarding, the system will automatically fetch
                    land records, satellite data, and weather information to compute the credit score.
                </p>
            </div>
        </div>
    );
};

export default FarmerOnboarding;
