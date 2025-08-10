'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { FileText, Upload, Download, Eye, X } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface Document {
  id: number
  name: string
  size: string
  type: string
  uploadDate: string
  url?: string
}

export function DocumentViewer() {
  const toast = useToast()
  const [documents, setDocuments] = useState<Document[]>([
    {
      id: 1,
      name: 'Specyfikacja_projektu.pdf',
      size: '2.3 MB',
      type: 'PDF',
      uploadDate: '2025-07-09',
      url: '/documents/spec.pdf'
    },
    {
      id: 2,
      name: 'Prezentacja_demo.pptx',
      size: '15.7 MB',
      type: 'PowerPoint',
      uploadDate: '2025-07-08',
    },
    {
      id: 3,
      name: 'Raport_miesięczny.docx',
      size: '1.1 MB',
      type: 'Word',
      uploadDate: '2025-07-07',
    },
  ])

  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null)
  const [isUploading, setIsUploading] = useState(false)

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (files) {
      setIsUploading(true)
      toast.loading('Przesyłanie plików...')
      
      // Symulacja uploadu
      setTimeout(() => {
        const newDocuments = Array.from(files).map((file, index) => ({
          id: documents.length + index + 1,
          name: file.name,
          size: `${(file.size / 1024 / 1024).toFixed(1)} MB`,
          type: file.type.includes('pdf') ? 'PDF' : 
                file.type.includes('word') ? 'Word' : 
                file.type.includes('presentation') ? 'PowerPoint' : 'Dokument',
          uploadDate: new Date().toISOString().split('T')[0],
        }))
        setDocuments([...documents, ...newDocuments])
        setIsUploading(false)
        toast.dismiss()
        toast.success(`Pomyślnie przesłano ${files.length} plik(ów)`)
      }, 2000)
    }
  }

  const getFileIcon = (type: string) => {
    return <FileText className="w-6 h-6 text-blue-600" />
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-gray-900">Dokumenty</h2>
        <motion.label
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer transition-colors flex items-center space-x-2"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Upload className="w-4 h-4" />
          <span>{isUploading ? 'Uploading...' : 'Upload pliku'}</span>
          <input
            type="file"
            className="hidden"
            multiple
            onChange={handleFileUpload}
            disabled={isUploading}
          />
        </motion.label>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {documents.map((doc) => (
          <motion.div
            key={doc.id}
            className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors cursor-pointer"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ scale: 1.02 }}
            onClick={() => setSelectedDocument(doc)}
          >
            <div className="flex items-start space-x-3">
              {getFileIcon(doc.type)}
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-gray-900 truncate">{doc.name}</h3>
                <p className="text-sm text-gray-500">{doc.type} • {doc.size}</p>
                <p className="text-xs text-gray-400 mt-1">Dodano: {doc.uploadDate}</p>
              </div>
            </div>
            <div className="flex items-center justify-end space-x-2 mt-3">
              <motion.button
                className="p-1 text-gray-400 hover:text-blue-600"
                whileHover={{ scale: 1.1 }}
                onClick={(e) => {
                  e.stopPropagation()
                  setSelectedDocument(doc)
                }}
              >
                <Eye className="w-4 h-4" />
              </motion.button>
              <motion.button
                className="p-1 text-gray-400 hover:text-green-600"
                whileHover={{ scale: 1.1 }}
                onClick={(e) => {
                  e.stopPropagation()
                  toast.success(`Pobieranie pliku: ${doc.name}`)
                  // TODO: Implementacja prawdziwego pobierania z API
                }}
              >
                <Download className="w-4 h-4" />
              </motion.button>
            </div>
          </motion.div>
        ))}
      </div>

      {isUploading && (
        <motion.div
          className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent"></div>
            <span className="text-sm text-blue-700">Uploading plików...</span>
          </div>
        </motion.div>
      )}

      {selectedDocument && (
        <motion.div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Podgląd dokumentu</h3>
              <button
                onClick={() => setSelectedDocument(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="space-y-3">
              <p><strong>Nazwa:</strong> {selectedDocument.name}</p>
              <p><strong>Typ:</strong> {selectedDocument.type}</p>
              <p><strong>Rozmiar:</strong> {selectedDocument.size}</p>
              <p><strong>Data dodania:</strong> {selectedDocument.uploadDate}</p>
            </div>
            <div className="mt-6 h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <div className="text-center text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-2" />
                <p>Podgląd dokumentu</p>
                <p className="text-sm">Funkcja podglądu będzie dostępna wkrótce</p>
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setSelectedDocument(null)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Zamknij
              </button>
              <button
                onClick={() => {
                  console.log('Downloading:', selectedDocument.name)
                  setSelectedDocument(null)
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Pobierz
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  )
}
