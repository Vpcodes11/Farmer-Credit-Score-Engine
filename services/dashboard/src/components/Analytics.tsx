import React, { useState, useEffect } from 'react';
import { farmersAPI } from '../api/client';

interface Analytics {
    totalFarmers: number;
    averageScore: number;
    scoreBands: {
        low: number;
        medium: number;
        high: number;
    };
}

const AnalyticsComponent: React.FC = () => {
    const [analytics, setAnalytics] = useState<Analytics>({
        totalFarmers: 0,
        averageScore: 0,
        scoreBands: { low: 0, medium: 0, high: 0 },
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadAnalytics();
    }, []);

    const loadAnalytics = async () => {
        setLoading(true);
        try {
            const response = await farmersAPI.getAll();
            const farmers = response.data;

            const totalFarmers = farmers.length;
            const farmersWithScores = farmers.filter((f: any) => f.latest_score);

            const averageScore = farmersWithScores.length > 0
                ? farmersWithScores.reduce((sum: number, f: any) => sum + f.latest_score.score, 0) / farmersWithScores.length
                : 0;

            const scoreBands = farmersWithScores.reduce(
                (acc: any, f: any) => {
                    acc[f.latest_score.score_band] = (acc[f.latest_score.score_band] || 0) + 1;
                    return acc;
                },
                { low: 0, medium: 0, high: 0 }
            );

            setAnalytics({
                totalFarmers,
                averageScore: Math.round(averageScore),
                scoreBands,
            });
        } catch (error) {
            console.error('Failed to load analytics:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="card">
                <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading analytics...</p>
                </div>
            </div>
        );
    }

    const totalWithScores = analytics.scoreBands.low + analytics.scoreBands.medium + analytics.scoreBands.high;

    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-800">Analytics Dashboard</h2>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="stat-card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Total Farmers</p>
                            <p className="text-3xl font-bold text-gray-900 mt-2">
                                {analytics.totalFarmers}
                            </p>
                        </div>
                        <div className="text-4xl">👨‍🌾</div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Average Score</p>
                            <p className="text-3xl font-bold text-gray-900 mt-2">
                                {analytics.averageScore}
                            </p>
                        </div>
                        <div className="text-4xl">📊</div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Scored Farmers</p>
                            <p className="text-3xl font-bold text-gray-900 mt-2">
                                {totalWithScores}
                            </p>
                        </div>
                        <div className="text-4xl">✅</div>
                    </div>
                </div>
            </div>

            {/* Score Distribution */}
            <div className="card">
                <h3 className="text-xl font-bold text-gray-800 mb-6">Score Band Distribution</h3>

                <div className="space-y-4">
                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-gray-700">High (70-100)</span>
                            <span className="text-sm font-semibold text-green-600">
                                {analytics.scoreBands.high} farmers
                            </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                            <div
                                className="bg-green-500 h-3 rounded-full transition-all duration-500"
                                style={{
                                    width: `${totalWithScores > 0 ? (analytics.scoreBands.high / totalWithScores) * 100 : 0}%`,
                                }}
                            ></div>
                        </div>
                    </div>

                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-gray-700">Medium (40-69)</span>
                            <span className="text-sm font-semibold text-yellow-600">
                                {analytics.scoreBands.medium} farmers
                            </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                            <div
                                className="bg-yellow-500 h-3 rounded-full transition-all duration-500"
                                style={{
                                    width: `${totalWithScores > 0 ? (analytics.scoreBands.medium / totalWithScores) * 100 : 0}%`,
                                }}
                            ></div>
                        </div>
                    </div>

                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-gray-700">Low (0-39)</span>
                            <span className="text-sm font-semibold text-red-600">
                                {analytics.scoreBands.low} farmers
                            </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                            <div
                                className="bg-red-500 h-3 rounded-full transition-all duration-500"
                                style={{
                                    width: `${totalWithScores > 0 ? (analytics.scoreBands.low / totalWithScores) * 100 : 0}%`,
                                }}
                            ></div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Insights */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="card bg-blue-50 border-blue-200">
                    <h4 className="font-semibold text-blue-900 mb-2">💡 Insight</h4>
                    <p className="text-sm text-blue-800">
                        {analytics.scoreBands.high > analytics.scoreBands.low
                            ? 'Majority of farmers have good credit scores, indicating healthy agricultural practices.'
                            : 'Focus on improving credit scores through better farming practices and financial literacy.'}
                    </p>
                </div>

                <div className="card bg-green-50 border-green-200">
                    <h4 className="font-semibold text-green-900 mb-2">📈 Opportunity</h4>
                    <p className="text-sm text-green-800">
                        {totalWithScores < analytics.totalFarmers
                            ? `${analytics.totalFarmers - totalWithScores} farmers pending credit score computation.`
                            : 'All farmers have been scored. Ready for loan processing!'}
                    </p>
                </div>
            </div>
        </div>
    );
};

export default AnalyticsComponent;
