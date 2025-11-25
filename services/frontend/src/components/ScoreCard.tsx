import React from 'react';

interface Driver {
    feature: string;
    impact: number;
    explanation: string;
}

interface ScoreCardProps {
    score: number;
    scoreBand: 'low' | 'medium' | 'high';
    drivers: Driver[];
}

const ScoreCard: React.FC<ScoreCardProps> = ({ score, scoreBand, drivers }) => {
    const getScoreColor = () => {
        switch (scoreBand) {
            case 'low':
                return 'score-low';
            case 'medium':
                return 'score-medium';
            case 'high':
                return 'score-high';
            default:
                return 'score-medium';
        }
    };

    const getImpactIcon = (impact: number) => {
        if (impact > 0) return '↑';
        if (impact < 0) return '↓';
        return '→';
    };

    const getImpactColor = (impact: number) => {
        if (impact > 0) return 'text-green-600';
        if (impact < 0) return 'text-red-600';
        return 'text-gray-600';
    };

    return (
        <div className="card">
            <div className="flex flex-col items-center mb-8">
                <h2 className="text-3xl font-bold text-gradient mb-6">Credit Score</h2>

                <div className={`score-gauge ${getScoreColor()}`}>
                    <div className="text-center">
                        <div className="text-5xl font-bold">{score}</div>
                        <div className="text-sm font-semibold uppercase tracking-wider mt-1">{scoreBand}</div>
                    </div>
                </div>

                <div className="mt-6 text-center">
                    <p className="text-sm text-gray-600 font-medium">
                        Score Range: 0-100
                    </p>
                </div>
            </div>

            <div className="border-t-2 border-gray-100 pt-8">
                <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                    <span className="text-2xl">📊</span>
                    Top Factors Affecting Score
                </h3>

                <div className="space-y-4">
                    {drivers.map((driver, index) => (
                        <div
                            key={index}
                            className={`p-5 bg-gradient-to-br from-white to-gray-50 rounded-xl border-2 border-gray-100 hover:border-emerald-200 hover:shadow-lg transition-all duration-300 animate-fade-in stagger-${index + 1}`}
                        >
                            <div className="flex items-start justify-between mb-3">
                                <h4 className="font-bold text-gray-800 flex-1 text-lg">
                                    {driver.feature}
                                </h4>
                                <span
                                    className={`text-2xl font-bold ml-3 ${getImpactColor(driver.impact)}`}
                                >
                                    {getImpactIcon(driver.impact)} {Math.abs(driver.impact)}
                                </span>
                            </div>
                            <p className="text-sm text-gray-600 leading-relaxed">{driver.explanation}</p>
                        </div>
                    ))}
                </div>
            </div>

            <div className="mt-8 p-6 bg-gradient-to-br from-emerald-50 to-green-50 rounded-xl border-2 border-emerald-200">
                <p className="text-sm text-emerald-900 leading-relaxed">
                    <strong className="text-emerald-700">💡 Transparency:</strong> This score is computed using satellite data,
                    weather patterns, and credit history. The factors above show the main drivers
                    affecting this farmer's creditworthiness.
                </p>
            </div>
        </div>
    );
};

export default ScoreCard;
