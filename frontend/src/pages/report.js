import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";

// Function to convert JSON data to CSV format
const convertToCSV = (data) => {
  const keys = Object.keys(data[0]);
  const csvRows = [];

  // Add headers
  csvRows.push(keys.join(','));

  // Add data rows
  data.forEach(row => {
    const values = keys.map(key => {
      let value = row[key];
      if (typeof value === 'string' && value.includes(',')) {
        // Remove commas from numbers represented as strings
        value = value.replace(/,/g, '');
      }
      return value;
    });
    csvRows.push(values.join(','));
  });

  return csvRows.join('\n');
};

// Function to trigger the download
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
  const { state } = useLocation();
  const { myData } = state || {};

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

  // Function to handle nested objects (flatten or format them)
  const formatCellValue = (value) => {
    if (typeof value === 'object' && value !== null) {
      return JSON.stringify(value, null, 2); // Pretty print JSON object
    }
    return value ?? "-"; // Handle null or undefined
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-600 to-teal-700">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl md:text-4xl font-bold text-white mb-8">Crediflow Report</h1>

        <div className="bg-white/95 rounded-lg shadow-xl p-6">
          <div className="max-w-md mb-8">
            <Select value={selectedReport} onValueChange={(value) => setSelectedReport(value)}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select a report" />
              </SelectTrigger>
              <SelectContent>
                {myData && Object.keys(myData).map((key) => (
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
          {reportData.length > 0 && (
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
  );
};

export default ReportPage;
