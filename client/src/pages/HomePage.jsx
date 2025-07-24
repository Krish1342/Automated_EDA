import { Link } from "react-router-dom";
import {
  Upload,
  BarChart3,
  Bot,
  Zap,
  CheckCircle,
  TrendingUp,
} from "lucide-react";

const HomePage = () => {
  const features = [
    {
      icon: <Upload className="w-8 h-8 text-blue-600" />,
      title: "Easy File Upload",
      description:
        "Simply drag and drop your CSV files to get started with automated analysis",
    },
    {
      icon: <Bot className="w-8 h-8 text-green-600" />,
      title: "AI-Powered Analysis",
      description:
        "Advanced AI algorithms automatically analyze your data and provide insights",
    },
    {
      icon: <BarChart3 className="w-8 h-8 text-purple-600" />,
      title: "Interactive Visualizations",
      description:
        "Beautiful, interactive charts and dashboards generated automatically",
    },
    {
      icon: <Zap className="w-8 h-8 text-orange-600" />,
      title: "Multiple Operations",
      description:
        "Clean, transform, classify, and visualize your data with just a few clicks",
    },
  ];

  const steps = [
    {
      number: "1",
      title: "Upload Your Data",
      description:
        "Upload your CSV file using our simple drag-and-drop interface",
    },
    {
      number: "2",
      title: "Choose Operation",
      description:
        "Select from data cleaning, transformation, classification, or visualization",
    },
    {
      number: "3",
      title: "Select Mode",
      description:
        "Choose between manual configuration or AI-powered automation",
    },
    {
      number: "4",
      title: "Get Results",
      description:
        "View your processed data, insights, and interactive visualizations",
    },
  ];

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <div className="text-center py-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Automated{" "}
          <span className="text-blue-600">Exploratory Data Analysis</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Transform your raw data into actionable insights with our
          comprehensive EDA platform. Upload, analyze, and visualize your data
          with the power of AI.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/upload"
            className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
          >
            <Upload className="w-5 h-5 mr-2" />
            Get Started
          </Link>
          <a
            href="#features"
            className="inline-flex items-center justify-center px-8 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors"
          >
            Learn More
          </a>
        </div>
      </div>

      {/* Features Section */}
      <section id="features" className="py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Powerful Features
          </h2>
          <p className="text-lg text-gray-600">
            Everything you need for comprehensive data analysis
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="text-center p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-center mb-4">{feature.icon}</div>
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it Works Section */}
      <section className="py-16 bg-gray-50 -mx-4 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-gray-600">
              Get insights from your data in four simple steps
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((step, index) => (
              <div key={index} className="text-center">
                <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg mx-auto mb-4">
                  {step.number}
                </div>
                <h3 className="text-lg font-semibold mb-2">{step.title}</h3>
                <p className="text-gray-600">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Why Choose AutoEDA?
          </h2>
          <p className="text-lg text-gray-600">
            Save time and discover insights faster
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center p-6">
            <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Save Time</h3>
            <p className="text-gray-600">
              Automate hours of manual data analysis work with AI-powered
              processing
            </p>
          </div>

          <div className="text-center p-6">
            <TrendingUp className="w-12 h-12 text-blue-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Better Insights</h3>
            <p className="text-gray-600">
              Discover patterns and relationships in your data that you might
              have missed
            </p>
          </div>

          <div className="text-center p-6">
            <BarChart3 className="w-12 h-12 text-purple-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Professional Results</h3>
            <p className="text-gray-600">
              Generate publication-ready charts and comprehensive analysis
              reports
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 text-center">
        <div className="bg-blue-600 text-white rounded-lg p-8">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Analyze Your Data?
          </h2>
          <p className="text-xl mb-6">
            Upload your CSV file and get comprehensive insights in minutes, not
            hours.
          </p>
          <Link
            to="/upload"
            className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-600 bg-white hover:bg-gray-100 transition-colors"
          >
            <Upload className="w-5 h-5 mr-2" />
            Start Your Analysis
          </Link>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
