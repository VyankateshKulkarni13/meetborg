import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { auth } from '@/services/api';

export default function Home() {
    const router = useRouter();
    const [checking, setChecking] = useState(true);

    useEffect(() => {
        const checkAuth = async () => {
            try {
                // Check if user is already logged in
                const token = localStorage.getItem('token');
                if (token) {
                    // Verify token is valid
                    await auth.getProfile();
                    router.push('/dashboard');
                    return;
                }

                // Check if this is the first user
                const response = await auth.checkFirstUser();
                const { is_first_user } = response.data;

                if (is_first_user) {
                    router.push('/register');
                } else {
                    router.push('/login');
                }
            } catch (error) {
                // If token verification fails, remove it and go to login
                localStorage.removeItem('token');
                router.push('/login');
            } finally {
                setChecking(false);
            }
        };

        checkAuth();
    }, [router]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-900">
            <div className="text-white text-xl">
                {checking ? 'Loading...' : 'Redirecting...'}
            </div>
        </div>
    );
}
