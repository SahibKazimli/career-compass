import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";

export default function NotFound() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900">
            <div className="text-center">
                <h1 className="text-4xl font-bold mb-4">404</h1>
                <p className="text-xl text-gray-600 dark:text-gray-400 mb-4">Page not found</p>
                <Link to="/">
                    <Button variant="outline" className="text-blue-500 hover:text-blue-700">
                        Return to Home
                    </Button>
                </Link>
            </div>
        </div>
    );
}
