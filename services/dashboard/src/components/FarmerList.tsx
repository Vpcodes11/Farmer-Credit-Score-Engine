import React, { useState, useEffect } from 'react';
import { farmersAPI } from '../api/client';

interface Farmer {
    id: string;
    farmer_id: string;
    name: string;
    mobile: string;
    created_at: string;
    latest_score?: {
        score: number;
        score_band: string;
    };
}

interface FarmerListProps {
    onSelectFarmer: (farmerId: string) => void;
}

const FarmerList: React.FC<FarmerListProps> = ({ onSelectFarmer }) => {
    const [farmers, setFarmers] = useState<Farmer[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterBand, setFilterBand] = useState<string>('all');

    useEffect(() => {
        loadFarmers();
    }, []);

    const loadFarmers = async () => {
        setLoading(true);
        try {
            const response = await farmersAPI.getAll();
            setFarmers(response.data);
        } catch (error) {
            console.error('Failed to load farmers:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredFarmers = farmers.filter((farmer) => {
        const matchesSearch =
            farmer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            farmer.farmer_id.toLowerCase().includes(searchTerm.toLowerCase());

        const matchesBand =
            filterBand === 'all' ||
            farmer.latest_score?.score_band === filterBand;

        return matchesSearch && matchesBand;
    });

    const getBadgeClass = (band: string) => {
        switch (band) {
            case 'low':
                return 'badge-low';
            case 'medium':
                return 'badge-medium';
            case 'high':
                return 'badge-high';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    if (loading) {
        return (
            <div className="card">
                <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading farmers...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="card">
            <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">All Farmers</h2>

                <div className="flex flex-col sm:flex-row gap-4">
                    <input
                        type="text"
                        placeholder="Search by name or ID..."
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />

                    <select
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        value={filterBand}
                        onChange={(e) => setFilterBand(e.target.value)}
                    >
                        <option value="all">All Score Bands</option>
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                    </select>
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead>
                        <tr>
                            <th className="table-header">Farmer ID</th>
                            <th className="table-header">Name</th>
                            <th className="table-header">Mobile</th>
                            <th className="table-header">Score</th>
                            <th className="table-header">Band</th>
                            <th className="table-header">Onboarded</th>
                            <th className="table-header">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {filteredFarmers.length === 0 ? (
                            <tr>
                                <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                                    No farmers found
                                </td>
                            </tr>
                        ) : (
                            filteredFarmers.map((farmer) => (
                                <tr key={farmer.id} className="hover:bg-gray-50">
                                    <td className="table-cell font-mono text-xs">
                                        {farmer.farmer_id}
                                    </td>
                                    <td className="table-cell font-semibold">
                                        {farmer.name}
                                    </td>
                                    <td className="table-cell text-gray-600">
                                        {farmer.mobile}
                                    </td>
                                    <td className="table-cell">
                                        {farmer.latest_score ? (
                                            <span className="font-bold text-lg">
                                                {farmer.latest_score.score}
                                            </span>
                                        ) : (
                                            <span className="text-gray-400">—</span>
                                        )}
                                    </td>
                                    <td className="table-cell">
                                        {farmer.latest_score ? (
                                            <span className={`badge ${getBadgeClass(farmer.latest_score.score_band)}`}>
                                                {farmer.latest_score.score_band}
                                            </span>
                                        ) : (
                                            <span className="text-gray-400 text-xs">No score</span>
                                        )}
                                    </td>
                                    <td className="table-cell text-gray-600 text-xs">
                                        {new Date(farmer.created_at).toLocaleDateString()}
                                    </td>
                                    <td className="table-cell">
                                        <button
                                            onClick={() => onSelectFarmer(farmer.farmer_id)}
                                            className="text-blue-600 hover:text-blue-800 font-medium text-sm"
                                        >
                                            View Details
                                        </button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            <div className="mt-4 text-sm text-gray-600">
                Showing {filteredFarmers.length} of {farmers.length} farmers
            </div>
        </div>
    );
};

export default FarmerList;
