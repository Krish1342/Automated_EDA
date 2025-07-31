import { useState } from "react";

const OperationSelector = ({ onSelectOperation, selectedFile }) => {
  const [selectedOperation, setSelectedOperation] = useState("");
  const [selectedMode, setSelectedMode] = useState("");
  const [showOptions, setShowOptions] = useState(false);
  const [options, setOptions] = useState({});

  const operations = [
    {
      id: "clean",
      title: "Data Cleaning",
      description: "Remove duplicates, handle missing values, fix data types",
      icon: "🧹",
      color: "bg-green-100 border-green-300 hover:bg-green-200",
    },
    {
      id: "transform",
      title: "Data Transformation",
      description: "Scale features, encode categories, create new features",
      icon: "🔄",
      color: "bg-blue-100 border-blue-300 hover:bg-blue-200",
    },
    {
      id: "classify",
      title: "Data Classification",
      description: "Analyze data types, patterns, and quality metrics",
      icon: "🏷️",
      color: "bg-purple-100 border-purple-300 hover:bg-purple-200",
    },
    {
      id: "visualize",
      title: "Data Visualization",
      description: "Generate comprehensive charts and dashboards",
      icon: "📊",
      color: "bg-orange-100 border-orange-300 hover:bg-orange-200",
    },
  ];

  const modes = [
    {
      id: "manual",
      title: "Manual Mode",
      description: "Configure specific operations and parameters",
      icon: <span>⚙️</span>,
      color: "bg-gray-100 border-gray-300 hover:bg-gray-200",
    },
    {
      id: "ai",
      title: "AI Mode",
      description: "Let AI automatically analyze and process your data",
      icon: <span>🤖</span>,
      color: "bg-indigo-100 border-indigo-300 hover:bg-indigo-200",
    },
  ];

  const handleOperationSelect = (operationId) => {
    setSelectedOperation(operationId);
    setSelectedMode(""); // Reset mode when operation changes
    setOptions({}); // Reset options when operation changes
    setShowOptions(true);
  };

  const handleModeSelect = (modeId) => {
    setSelectedMode(modeId);
    if (modeId === "manual") {
      setShowOptions(true);
    } else {
      const defaultOpts = getDefaultOptions(selectedOperation);
      setOptions(defaultOpts);
      setShowOptions(false);
      handleSubmit(modeId, defaultOpts); // AI mode auto-submits
    }
  };

  const handleSubmit = (mode = selectedMode, opts = options) => {
    if (selectedOperation && mode) {
      onSelectOperation({
        operation: selectedOperation,
        mode: mode,
        options: opts,
        fileId: selectedFile.file_id,
      });
    }
  };

  const getDefaultOptions = (operation) => {
    switch (operation) {
      case "clean":
        return {
          missing_strategy: "drop",
          drop_columns: [],
        };
      case "transform":
        return {
          encoding_method: "none",
          scaling_method: "standard",
        };
      case "classify":
        return {
          target_column: "",
          classifier_type: "logistic",
        };
      case "visualize":
        return {
          chart_types: "all",
        };
      default:
        return {};
    }
  };

  const renderOptions = () => {
    if (!showOptions) return null;

    switch (selectedOperation) {
      case "clean":
        return (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg space-y-4">
            <div>
              <label className="form-label">Missing Value Strategy</label>
              <select
                className="form-input"
                value={options.missing_strategy || "drop"}
                onChange={(e) =>
                  setOptions({ ...options, missing_strategy: e.target.value })
                }
              >
                <option value="drop">Drop Rows</option>
                <option value="mean">Fill with Mean</option>
                <option value="median">Fill with Median</option>
                <option value="most_frequent">Fill with Mode</option>
              </select>
            </div>
            <button onClick={() => handleSubmit()} className="btn-primary">
              Start Cleaning
            </button>
          </div>
        );
      case "transform":
        return (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg space-y-4">
            <div>
              <label className="form-label">Scaling Method</label>
              <select
                className="form-input"
                value={options.scaling_method || "none"}
                onChange={(e) =>
                  setOptions({ ...options, scaling_method: e.target.value })
                }
              >
                <option value="none">No Scaling</option>
                <option value="standard">Standard Scaling</option>
                <option value="minmax">Min-Max Scaling</option>
              </select>
            </div>
            <div>
              <label className="form-label">Encoding Method</label>
              <select
                className="form-input"
                value={options.encoding_method || "none"}
                onChange={(e) =>
                  setOptions({ ...options, encoding_method: e.target.value })
                }
              >
                <option value="none">No Encoding</option>
                <option value="label">Label Encoding</option>
                <option value="onehot">One-Hot Encoding</option>
              </select>
            </div>
            <button onClick={() => handleSubmit()} className="btn-primary">
              Start Transformation
            </button>
          </div>
        );

      case "classify":
        return (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg space-y-4">
            <div>
              <label className="form-label">Classifier Type</label>
              <select
                className="form-input"
                value={options.classifier_type || "logistic"}
                onChange={(e) =>
                  setOptions({ ...options, classifier_type: e.target.value })
                }
              >
                <option value="logistic">Logistic Regression</option>
                <option value="knn">K-Nearest Neighbors</option>
                <option value="decision_tree">Decision Tree</option>
              </select>
            </div>
            <div>
              <label className="form-label">Target Column</label>
              <input
                className="form-input"
                type="text"
                placeholder="Enter target column name"
                value={options.target_column || ""}
                onChange={(e) =>
                  setOptions({ ...options, target_column: e.target.value })
                }
              />
            </div>
            <button onClick={() => handleSubmit()} className="btn-primary">
              Start Classification
            </button>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Choose Operation</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {operations.map((operation) => (
            <div
              key={operation.id}
              onClick={() => handleOperationSelect(operation.id)}
              className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                selectedOperation === operation.id
                  ? "border-blue-500 bg-blue-50"
                  : operation.color
              }`}
            >
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{operation.icon}</span>
                <div>
                  <h4 className="font-semibold">{operation.title}</h4>
                  <p className="text-sm text-gray-600">{operation.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedOperation && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Choose Mode</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {modes.map((mode) => (
              <div
                key={mode.id}
                onClick={() => handleModeSelect(mode.id)}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  selectedMode === mode.id
                    ? "border-blue-500 bg-blue-50"
                    : mode.color
                }`}
              >
                <div className="flex items-center space-x-3">
                  {mode.icon}
                  <div>
                    <h4 className="font-semibold">{mode.title}</h4>
                    <p className="text-sm text-gray-600">{mode.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {renderOptions()}
    </div>
  );
};

export default OperationSelector;
