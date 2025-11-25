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
            <div className="flex flex-col items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">Credit Score</h2>

                <div className={`score-gauge ${getScoreColor()}`}>
                    <div className="text-center">
                        <div className="text-4xl font-bold">{score}</div>
                        <div className="text-sm font-medium uppercase">{scoreBand}</div>
                    </div>
                </div>

                <div className="mt-4 text-center">
                    <p className="text-sm text-gray-600">
                        Score Range: 0-100
                    </p>
                </div>
            </div>

            <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">
                    Top Factors Affecting Score
                </h3>

                <div className="space-y-4">
                    {drivers.map((driver, index) => (
                        <div
                            key={index}
                            className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                        >
                            <div className="flex items-start justify-between mb-2">
                                <h4 className="font-semibold text-gray-800 flex-1">
                                    {driver.feature}
                                </h4>
                                <span
                                    className={`text-xl font-bold ml-2 ${getImpactColor(driver.impact)}`}
                                >
                                    {getImpactIcon(driver.impact)} {Math.abs(driver.impact)}
                                </span>
                            </div>
                            <p className="text-sm text-gray-600">{driver.explanation}</p>
                        </div>
                    ))}
                </div>
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm text-blue-800">
                    <strong>💡 Transparency:</strong> This score is computed using satellite data,
                    weather patterns, and credit history. The factors above show the main drivers
                    affecting this farmer's creditworthiness.
                </p>
            </div>
        </div>
    );
};

export default ScoreCard;
