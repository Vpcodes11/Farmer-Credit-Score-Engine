import React, { useState, useEffect } from 'react';
import { farmersAPI, scoringAPI, loanAPI } from '../api/client';
import ScoreCard from './ScoreCard';

interface FarmerProfileProps {
    farmerId: string;
}

interface FarmerData {
    id: string;
    farmer_id: string;
    name: string;
    mobile: string;
    created_at: string;
    latest_score?: {
        score: number;
        score_band: string;
        drivers: Array<{
            feature: string;
            impact: number;
            explanation: string;
        }>;
    };
}

interface LoanQuote {
    eligible: boolean;
    max_loan_amount: number;
    recommended_amount: number;
    emi_plans: Array<{
        tenure_months: number;
        monthly_emi: number;
        total_interest: number;
    }>;
}

const FarmerProfile: React.FC<FarmerProfileProps> = ({ farmerId }) => {
    const [farmer, setFarmer] = useState<FarmerData | null>(null);
    const [loanQuote, setLoanQuote] = useState<LoanQuote | null>(null);
    const [loading, setLoading] = useState(true);
    const [computingScore, setComputingScore] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadFarmerData();
    }, [farmerId]);

    const loadFarmerData = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await farmersAPI.getById(farmerId);
            setFarmer(response.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load farmer data');
        } finally {
            setLoading(false);
        }
    };

    const computeScore = async () => {
        setComputingScore(true);
        setError(null);

        try {
            const response = await scoringAPI.computeScore(farmerId);

            // Reload farmer data to get updated score
            await loadFarmerData();

            // Get loan quote
            if (response.data.score >= 50) {
                const loanResponse = await loanAPI.getQuote({
                    farmer_id: farmerId,
                    loan_amount: 100000,
                    crop_type: 'wheat',
                });
                setLoanQuote(loanResponse.data);
            }
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to compute score');
        } finally {
            setComputingScore(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading farmer profile...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card max-w-2xl mx-auto mt-8">
                <div className="text-center text-red-600">
                    <p className="text-lg font-semibold mb-2">Error</p>
                    <p>{error}</p>
                    <button onClick={loadFarmerData} className="btn-primary mt-4">
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    if (!farmer) {
        return (
            <div className="card max-w-2xl mx-auto mt-8">
                <p className="text-center text-gray-600">Farmer not found</p>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto space-y-6 p-4">
            {/* Farmer Info Card */}
            <div className="card">
                <div className="flex items-start justify-between mb-4">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-800">{farmer.name}</h1>
                        <p className="text-gray-600 mt-1">ID: {farmer.farmer_id}</p>
                    </div>
                    <div className="text-right">
                        <p className="text-sm text-gray-600">Mobile</p>
                        <p className="font-semibold text-gray-800">{farmer.mobile}</p>
                    </div>
                </div>

                <div className="pt-4 border-t border-gray-200">
                    <p className="text-sm text-gray-600">
                        Onboarded: {new Date(farmer.created_at).toLocaleDateString('en-IN', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                        })}
                    </p>
                </div>
            </div>

            {/* Score Section */}
            {farmer.latest_score ? (
                <ScoreCard
                    score={farmer.latest_score.score}
                    scoreBand={farmer.latest_score.score_band as 'low' | 'medium' | 'high'}
                    drivers={farmer.latest_score.drivers}
                />
            ) : (
                <div className="card text-center">
                    <h2 className="text-xl font-semibold text-gray-800 mb-4">
                        No Credit Score Yet
                    </h2>
                    <p className="text-gray-600 mb-6">
                        Compute the credit score to assess loan eligibility
                    </p>
                    <button
                        onClick={computeScore}
                        disabled={computingScore}
                        className="btn-primary"
                    >
                        {computingScore ? 'Computing Score...' : 'Compute Credit Score'}
                    </button>
                </div>
            )}

            {/* Loan Eligibility */}
            {loanQuote && (
                <div className="card">
                    <h2 className="text-2xl font-bold text-gray-800 mb-4">
                        Loan Eligibility
                    </h2>

                    {loanQuote.eligible ? (
                        <>
                            <div className="grid grid-cols-2 gap-4 mb-6">
                                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                                    <p className="text-sm text-gray-600 mb-1">Max Loan Amount</p>
                                    <p className="text-2xl font-bold text-green-700">
                                        ₹{loanQuote.max_loan_amount.toLocaleString('en-IN')}
                                    </p>
                                </div>
                                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                                    <p className="text-sm text-gray-600 mb-1">Recommended</p>
                                    <p className="text-2xl font-bold text-blue-700">
                                        ₹{loanQuote.recommended_amount.toLocaleString('en-IN')}
                                    </p>
                                </div>
                            </div>

                            <h3 className="font-semibold text-gray-800 mb-3">EMI Plans</h3>
                            <div className="space-y-3">
                                {loanQuote.emi_plans.map((plan, index) => (
                                    <div
                                        key={index}
                                        className="p-4 bg-gray-50 rounded-lg border border-gray-200 flex justify-between items-center"
                                    >
                                        <div>
                                            <p className="font-semibold text-gray-800">
                                                {plan.tenure_months} Months
                                            </p>
                                            <p className="text-sm text-gray-600">
                                                Total Interest: ₹{plan.total_interest.toLocaleString('en-IN')}
                                            </p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-sm text-gray-600">Monthly EMI</p>
                                            <p className="text-xl font-bold text-gray-800">
                                                ₹{plan.monthly_emi.toLocaleString('en-IN')}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </>
                    ) : (
                        <div className="text-center p-6 bg-yellow-50 rounded-lg border border-yellow-200">
                            <p className="text-yellow-800">
                                Not eligible for loan at this time. Improve credit score to qualify.
                            </p>
                        </div>
                    )}
                </div>
            )}

            {/* Refresh Score Button */}
            {farmer.latest_score && (
                <div className="text-center">
                    <button
                        onClick={computeScore}
                        disabled={computingScore}
                        className="btn-secondary"
                    >
                        {computingScore ? 'Refreshing...' : 'Refresh Score'}
                    </button>
                </div>
            )}
        </div>
    );
};

export default FarmerProfile;
