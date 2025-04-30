import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";

const convertToCSV = (data) => {
  const keys = Object.keys(data[0]);
  const csvRows = [];

  csvRows.push(keys.join(','));

  data.forEach(row => {
    const values = keys.map(key => {
      let value = row[key];
      if (typeof value === 'string' && value.includes(',')) {
        value = value.replace(/,/g, '');
      }
      return value;
    });
    csvRows.push(values.join(','));
  });

  return csvRows.join('\n');
};

const downloadCSV = (data, fileName) => {
  const csvData = convertToCSV(data);
  const blob = new Blob([csvData], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName || 'report.csv';
  a.click();
  window.URL.revokeObjectURL(url);
};

const ReportPage = () => {
  const [selectedReport, setSelectedReport] = useState('');
  const [tableColumns, setTableColumns] = useState([]);
  const [reportData, setReportData] = useState({});
  const [vocabVisible, setVocabVisible] = useState(false);
  const { state } = useLocation();
  const { myData } = state || {};

  const vocabularyData = myData?.vocabulary ? JSON.parse(myData.vocabulary) : [];

  useEffect(() => {
    if (selectedReport && myData[selectedReport]) {
      const parsedData = JSON.parse(myData[selectedReport]);

      const columnsSet = new Set();
      if (Array.isArray(parsedData)) {
        parsedData.forEach(item => {
          Object.keys(item).forEach(key => {
            if (key !== "Particular") {
              columnsSet.add(key);
            }
          });
        });
      }

      setTableColumns(Array.from(columnsSet));
      setReportData(parsedData);
    }
  }, [selectedReport, myData]);

  const formatCellValue = (value) => {
    if (typeof value === 'object' && value !== null) {
      return JSON.stringify(value, null, 2);
    }
    return value ?? "-";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-600 to-teal-700">
      <div className="container mx-auto px-4 py-8 flex flex-col lg:flex-row gap-8">
        {/* Left Content */}
        <div className="flex-1">
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-8">Crediflow Report</h1>
          <div className="bg-white/95 rounded-lg shadow-xl p-6">
            <div className="max-w-md mb-8">
              <Select value={selectedReport} onValueChange={(value) => setSelectedReport(value)}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select a report" />
                </SelectTrigger>
                <SelectContent>
                  {myData &&
                    Object.keys(myData)
                      .filter((key) => key !== "vocabulary")
                      .map((key) => (
                        <SelectItem key={key} value={key}>
                          {key}
                        </SelectItem>
                      ))}
                </SelectContent>
              </Select>
            </div>

            {selectedReport && reportData ? (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Particular</TableHead>
                      {tableColumns.map((col) => (
                        <TableHead key={col}>{col}</TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {Array.isArray(reportData) ? (
                      reportData.map((row, index) => (
                        <TableRow key={index}>
                          <TableCell>{row.Particular}</TableCell>
                          {tableColumns.map((col) => (
                            <TableCell key={col}>
                              {formatCellValue(row[col])}
                            </TableCell>
                          ))}
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell>{reportData.Particular}</TableCell>
                        {tableColumns.map((col) => (
                          <TableCell key={col}>
                            {formatCellValue(reportData[col])}
                          </TableCell>
                        ))}
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            ) : (
              <div className="text-center text-white">
                <p>No data available for the selected report.</p>
              </div>
            )}

            {/* Download Button */}
            {Array.isArray(reportData) && reportData.length > 0 && (
              <button
                onClick={() => downloadCSV(reportData, 'report.csv')}
                className="mt-4 bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-700"
              >
                Download CSV
              </button>
            )}
          </div>
        </div>


      </div>

      {/* Vocabulary Button and Panel Below Table */}
      <div className="mt-6">
        <div className="flex justify-center">
          <button
            onClick={() => setVocabVisible(!vocabVisible)}
            className="bg-white text-emerald-700 font-semibold px-6 py-3 text-lg rounded-lg shadow hover:bg-emerald-100 transition-all duration-200"
          >
            {vocabVisible ? "Hide Vocabulary" : "Show Changed Vocabulary"}
          </button>
        </div>

        {vocabVisible && (
          <div className="mt-6 max-w-full sm:max-w-3xl mx-auto bg-white/90 rounded-lg shadow-lg p-6 max-h-[70vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">Changed Vocabulary List</h2>
            <h4 className="text-3xs font-medium mb-1">Older Vocabulary</h4>
            <h4 className="text-2xs font-light mb-4">Newer Vocabulary</h4>

            {vocabularyData.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {vocabularyData.map((item, index) => (
                  <div key={index} className="border p-2 rounded">
                    <p className="font-semibold">{item.term || "—"}</p>
                    <p className="text-sm text-gray-600">{item.definition || "-"}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600">No vocabulary data found.</p>
            )}
          </div>
        )}
      </div>





    </div>
  );
};

export default ReportPage;
