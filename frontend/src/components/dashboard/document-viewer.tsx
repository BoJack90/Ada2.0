'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  FileText, 
  Upload, 
  Download, 
  Search, 
  Filter, 
  Eye, 
  Edit, 
  Trash2,
  Plus,
  File,
  Image,
  FileSpreadsheet,
  FolderPlus,
  HardDrive
} from 'lucide-react'

interface Document {
  id: string
  name: string
  type: 'pdf' | 'doc' | 'txt' | 'xlsx' | 'img'
  size: string
  modified: string
  owner: string
}

export function DocumentViewer() {
  const [searchTerm, setSearchTerm] = useState('')
  const [documents] = useState<Document[]>([
    {
      id: '1',
      name: 'Project_Requirements.pdf',
      type: 'pdf',
      size: '2.4 MB',
      modified: '2024-01-15',
      owner: 'Admin'
    },
    {
      id: '2',
      name: 'Meeting_Notes.doc',
      type: 'doc',
      size: '845 KB',
      modified: '2024-01-14',
      owner: 'User1'
    },
    {
      id: '3',
      name: 'Budget_Analysis.xlsx',
      type: 'xlsx',
      size: '1.2 MB',
      modified: '2024-01-13',
      owner: 'User2'
    },
    {
      id: '4',
      name: 'Company_Logo.png',
      type: 'img',
      size: '156 KB',
      modified: '2024-01-12',
      owner: 'Designer'
    }
  ])

  const getFileIconWithStyles = (type: string) => {
    switch (type) {
      case 'pdf':
        return { 
          icon: FileText, 
          color: 'text-red-500', 
          bg: 'bg-red-100',
          border: 'border-red-200'
        }
      case 'doc':
        return { 
          icon: FileText, 
          color: 'text-blue-500', 
          bg: 'bg-blue-100',
          border: 'border-blue-200'
        }
      case 'txt':
        return { 
          icon: File, 
          color: 'text-gray-500', 
          bg: 'bg-gray-100',
          border: 'border-gray-200'
        }
      case 'xlsx':
        return { 
          icon: FileSpreadsheet, 
          color: 'text-emerald-500', 
          bg: 'bg-emerald-100',
          border: 'border-emerald-200'
        }
      case 'img':
        return { 
          icon: Image, 
          color: 'text-purple-500', 
          bg: 'bg-purple-100',
          border: 'border-purple-200'
        }
      default:
        return { 
          icon: File, 
          color: 'text-gray-500', 
          bg: 'bg-gray-100',
          border: 'border-gray-200'
        }
    }
  }

  const filteredDocuments = documents.filter(doc =>
    doc.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-6">
      {/* Modern Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="mb-8"
      >
        <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-700 rounded-2xl p-8 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                className="p-3 bg-white/20 rounded-xl backdrop-blur-sm"
              >
                <FileText className="h-8 w-8" />
              </motion.div>
              <div>
                <h1 className="text-3xl font-bold">Documents</h1>
                <p className="text-indigo-100 mt-2">Centralne repozytorium plików i dokumentów</p>
              </div>
            </div>
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-6 py-3 bg-white/20 rounded-xl backdrop-blur-sm hover:bg-white/30 transition-colors flex items-center space-x-2"
            >
              <Upload className="h-5 w-5" />
              <span>Upload Document</span>
            </motion.button>
          </div>
        </div>
      </motion.div>

      <div className="space-y-8">
        {/* Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <input
                type="text"
                className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="Search documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="flex justify-end space-x-3">
              <motion.button 
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="px-4 py-3 bg-gradient-to-r from-gray-50 to-slate-50 hover:from-gray-100 hover:to-slate-100 border border-gray-200 rounded-xl transition-all flex items-center space-x-2"
              >
                <Filter className="h-4 w-4" />
                <span>Filter</span>
              </motion.button>
              <motion.button 
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="px-4 py-3 bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 border border-blue-200 rounded-xl transition-all flex items-center space-x-2 text-blue-700"
              >
                <FolderPlus className="h-4 w-4" />
                <span>New Folder</span>
              </motion.button>
            </div>
          </div>
        </motion.div>

        {/* Documents List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden"
        >
          <div className="bg-gradient-to-r from-emerald-500 to-teal-600 p-6 text-white">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-semibold">All Documents ({filteredDocuments.length})</h2>
                <p className="text-emerald-100">
                  {documents.reduce((total, doc) => total + parseFloat(doc.size), 0).toFixed(1)} MB total
                </p>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            {filteredDocuments.length > 0 ? (
              <div className="space-y-4">
                {filteredDocuments.map((doc, index) => {
                  const fileStyles = getFileIconWithStyles(doc.type)
                  const IconComponent = fileStyles.icon
                  
                  return (
                    <motion.div
                      key={doc.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.4 + index * 0.1 }}
                      whileHover={{ scale: 1.01, y: -2 }}
                      className={`p-4 rounded-xl border ${fileStyles.border} ${fileStyles.bg} hover:shadow-md transition-all duration-300`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className={`p-3 bg-white rounded-xl ${fileStyles.color} shadow-sm`}>
                            <IconComponent className="h-6 w-6" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900">{doc.name}</h3>
                            <div className="flex items-center space-x-4 text-sm text-gray-600">
                              <span>{doc.size}</span>
                              <span>•</span>
                              <span>{doc.modified}</span>
                              <span>•</span>
                              <span>by {doc.owner}</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <motion.button 
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="View"
                          >
                            <Eye className="h-4 w-4" />
                          </motion.button>
                          <motion.button 
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            className="p-2 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                            title="Edit"
                          >
                            <Edit className="h-4 w-4" />
                          </motion.button>
                          <motion.button 
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            className="p-2 text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors"
                            title="Download"
                          >
                            <Download className="h-4 w-4" />
                          </motion.button>
                          <motion.button 
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="h-4 w-4" />
                          </motion.button>
                        </div>
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            ) : (
              <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4 }}
                className="text-center py-12 bg-gradient-to-br from-gray-50 to-blue-50 rounded-2xl border border-gray-100"
              >
                <FileText size={80} className="text-blue-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No documents found</h3>
                <p className="text-gray-600 mb-6">
                  {searchTerm ? 'Try adjusting your search terms' : 'Upload your first document to get started'}
                </p>
                <motion.button 
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all flex items-center space-x-2 mx-auto"
                >
                  <Upload className="h-5 w-5" />
                  <span>Upload Document</span>
                </motion.button>
              </motion.div>
            )}
          </div>
        </motion.div>

        {/* Storage Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden"
        >
          <div className="bg-gradient-to-r from-orange-500 to-red-600 p-6 text-white">
            <div className="flex items-center space-x-3">
              <HardDrive className="h-6 w-6" />
              <div>
                <h2 className="text-xl font-semibold">Storage Information</h2>
                <p className="text-orange-100">Przegląd wykorzystania przestrzeni dyskowej</p>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="text-center p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-100"
              >
                <div className="text-3xl font-bold text-blue-600 mb-2">15.2 GB</div>
                <p className="text-sm text-blue-700 font-medium">Used Storage</p>
              </motion.div>
              
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="text-center p-4 bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl border border-emerald-100"
              >
                <div className="text-3xl font-bold text-emerald-600 mb-2">34.8 GB</div>
                <p className="text-sm text-emerald-700 font-medium">Available</p>
              </motion.div>
              
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
                className="text-center p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-100"
              >
                <div className="text-3xl font-bold text-purple-600 mb-2">50 GB</div>
                <p className="text-sm text-purple-700 font-medium">Total Storage</p>
              </motion.div>
              
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
                className="text-center p-4 bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl border border-yellow-100"
              >
                <div className="text-3xl font-bold text-yellow-600 mb-2">124</div>
                <p className="text-sm text-yellow-700 font-medium">Total Files</p>
              </motion.div>
            </div>
            
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.9 }}
              className="space-y-2"
            >
              <div className="flex justify-between text-sm text-gray-600">
                <span>Storage Usage</span>
                <span>30.4% used</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: '30.4%' }}
                  transition={{ delay: 1, duration: 1 }}
                  className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full"
                />
              </div>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
