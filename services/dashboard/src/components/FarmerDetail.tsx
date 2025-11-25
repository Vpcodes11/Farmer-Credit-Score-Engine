import React, { useState, useEffect } from 'react';
import { farmersAPI, scoringAPI } from '../api/client';

interface FarmerDetailProps {
    farmerId: string;
    onBack: () => void;
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

const FarmerDetail: React.FC<FarmerDetailProps> = ({ farmerId, onBack }) => {
    const [farmer, setFarmer] = useState<FarmerData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadFarmerDetail();
    }, [farmerId]);

    const loadFarmerDetail = async () => {
        setLoading(true);
        try {
            const response = await farmersAPI.getById(farmerId);
            setFarmer(response.data);
        } catch (error) {
            console.error('Failed to load farmer details:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="card">
                <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading farmer details...</p>
                </div>
            </div>
        );
    }

    if (!farmer) {
        return (
            <div className="card">
                <p className="text-center text-gray-600">Farmer not found</p>
                <button onClick={onBack} className="btn-secondary mt-4 mx-auto block">
                    Go Back
                </button>
            </div>
        );
    }

    const getScoreColor = (band: string) => {
        switch (band) {
            case 'low':
                return 'text-red-600 bg-red-50 border-red-200';
            case 'medium':
                return 'text-yellow-600 bg-yellow-50 border-yellow-200';
            case 'high':
                return 'text-green-600 bg-green-50 border-green-200';
            default:
                return 'text-gray-600 bg-gray-50 border-gray-200';
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <button onClick={onBack} className="btn-secondary">
                    ← Back to List
                </button>
            </div>

            {/* Farmer Info */}
            <div className="card">
                <div className="flex items-start justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-800">{farmer.name}</h1>
                        <p className="text-gray-600 mt-1 font-mono text-sm">ID: {farmer.farmer_id}</p>
                    </div>
                    <div className="text-right">
                        <p className="text-sm text-gray-600">Mobile</p>
                        <p className="font-semibold text-gray-800">{farmer.mobile}</p>
                    </div>
                </div>

                <div className="mt-6 pt-6 border-t border-gray-200">
                    <p className="text-sm text-gray-600">
                        Onboarded: {new Date(farmer.created_at).toLocaleDateString('en-IN', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                        })}
                    </p>
                </div>
            </div>

            {/* Credit Score */}
            {farmer.latest_score ? (
                <>
                    <div className="card">
                        <h2 className="text-2xl font-bold text-gray-800 mb-6">Credit Score</h2>

                        <div className="flex items-center gap-8 mb-8">
                            <div className={`flex-shrink-0 w-32 h-32 rounded-full border-4 flex items-center justify-center ${getScoreColor(farmer.latest_score.score_band)}`}>
                                <div className="text-center">
                                    <div className="text-4xl font-bold">{farmer.latest_score.score}</div>
                                    <div className="text-xs font-medium uppercase mt-1">
                                        {farmer.latest_score.score_band}
                                    </div>
                                </div>
                            </div>

                            <div className="flex-1">
                                <h3 className="font-semibold text-gray-800 mb-2">Score Interpretation</h3>
                                <p className="text-sm text-gray-600">
                                    {farmer.latest_score.score_band === 'high' &&
                                        'Excellent creditworthiness. Eligible for premium loan products with favorable terms.'}
                                    {farmer.latest_score.score_band === 'medium' &&
                                        'Good creditworthiness. Eligible for standard loan products.'}
                                    {farmer.latest_score.score_band === 'low' &&
                                        'Limited creditworthiness. May require collateral or guarantor for loan approval.'}
                                </p>
                            </div>
                        </div>

                        <div className="border-t border-gray-200 pt-6">
                            <h3 className="text-lg font-semibold text-gray-800 mb-4">
                                Top Factors Affecting Score
                            </h3>

                            <div className="space-y-4">
                                {farmer.latest_score.drivers.map((driver, index) => (
                                    <div
                                        key={index}
                                        className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                                    >
                                        <div className="flex items-start justify-between mb-2">
                                            <h4 className="font-semibold text-gray-800 flex-1">
                                                {driver.feature}
                                            </h4>
                                            <span
                                                className={`text-xl font-bold ml-2 ${driver.impact > 0
                                                        ? 'text-green-600'
                                                        : driver.impact < 0
                                                            ? 'text-red-600'
                                                            : 'text-gray-600'
                                                    }`}
                                            >
                                                {driver.impact > 0 ? '↑' : driver.impact < 0 ? '↓' : '→'}{' '}
                                                {Math.abs(driver.impact)}
                                            </span>
                                        </div>
                                        <p className="text-sm text-gray-600">{driver.explanation}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Loan Recommendation */}
                    <div className="card bg-blue-50 border-blue-200">
                        <h3 className="text-lg font-semibold text-blue-900 mb-3">
                            💼 Loan Recommendation
                        </h3>
                        <p className="text-sm text-blue-800">
                            {farmer.latest_score.score >= 70 &&
                                'Recommended for loan approval up to ₹2,00,000 with standard interest rates.'}
                            {farmer.latest_score.score >= 40 && farmer.latest_score.score < 70 &&
                                'Recommended for loan approval up to ₹1,00,000 with moderate interest rates.'}
                            {farmer.latest_score.score < 40 &&
                                'Recommend financial literacy program and micro-credit products to build credit history.'}
                        </p>
                    </div>
                </>
            ) : (
                <div className="card text-center py-12">
                    <p className="text-gray-600 mb-4">No credit score available for this farmer</p>
                    <p className="text-sm text-gray-500">
                        Score will be computed when the farmer is onboarded through the field agent app
                    </p>
                </div>
            )}
        </div>
    );
};

export default FarmerDetail;
