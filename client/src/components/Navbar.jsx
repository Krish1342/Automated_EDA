import { Link, useLocation } from "react-router-dom";
import { BarChart3, Upload, Home, FileText } from "lucide-react";

const Navbar = () => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path ? "bg-blue-700" : "hover:bg-blue-700";
  };

  return (
    <nav className="bg-blue-600 shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <Link
            to="/"
            className="flex items-center space-x-2 text-white text-xl font-bold"
          >
            <BarChart3 className="w-8 h-8" />
            <span>AutoEDA</span>
          </Link>

          <div className="flex space-x-1">
            <Link
              to="/"
              className={`flex items-center space-x-2 px-4 py-2 rounded-md text-white transition-colors ${isActive(
                "/"
              )}`}
            >
              <Home className="w-4 h-4" />
              <span>Home</span>
            </Link>

            <Link
              to="/upload"
              className={`flex items-center space-x-2 px-4 py-2 rounded-md text-white transition-colors ${isActive(
                "/upload"
              )}`}
            >
              <Upload className="w-4 h-4" />
              <span>Upload Data</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
