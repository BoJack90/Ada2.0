'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { User, Mail, Lock, FileText, Save } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/cards'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { FadeIn, SlideIn, StaggerChildren, StaggerItem } from '@/components/ui/animations'

export function ExampleForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    category: '',
    description: ''
  })
  const [showDialog, setShowDialog] = useState(false)
  
  const categoryOptions = [
    { value: 'blog', label: 'Blog Post', icon: <FileText className="h-4 w-4" />, description: 'Long-form content' },
    { value: 'social', label: 'Social Media', description: 'Short, engaging posts' },
    { value: 'email', label: 'Email Campaign', icon: <Mail className="h-4 w-4" />, description: 'Newsletter content' },
  ]
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setShowDialog(true)
  }
  
  return (
    <>
      <FadeIn>
        <Card className="max-w-2xl mx-auto">
          <div className="p-6">
            <SlideIn direction="down">
              <h2 className="text-2xl font-bold text-foreground mb-2">Create New Content</h2>
              <p className="text-muted-foreground mb-6">Fill out the form below to create your content plan</p>
            </SlideIn>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <StaggerChildren>
                <StaggerItem>
                  <Input
                    label="Content Name"
                    placeholder="Enter a name for your content"
                    icon={<User className="h-4 w-4" />}
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                    hint="Choose a descriptive name"
                  />
                </StaggerItem>
                
                <StaggerItem>
                  <Input
                    label="Email"
                    type="email"
                    placeholder="your@email.com"
                    icon={<Mail className="h-4 w-4" />}
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                  />
                </StaggerItem>
                
                <StaggerItem>
                  <Select
                    label="Content Category"
                    options={categoryOptions}
                    value={formData.category}
                    onChange={(value) => setFormData({ ...formData, category: value })}
                    placeholder="Select a category"
                    hint="This helps us optimize the content"
                  />
                </StaggerItem>
                
                <StaggerItem>
                  <Textarea
                    label="Description"
                    placeholder="Describe your content plan..."
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    showCharCount
                    maxLength={500}
                    hint="Provide details about your content goals"
                    className="min-h-[150px]"
                  />
                </StaggerItem>
                
                <StaggerItem>
                  <div className="flex gap-3 pt-4">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setFormData({ name: '', email: '', category: '', description: '' })}
                    >
                      Clear
                    </Button>
                    <Button type="submit" className="flex-1">
                      <Save className="h-4 w-4 mr-2" />
                      Create Content Plan
                    </Button>
                  </div>
                </StaggerItem>
              </StaggerChildren>
            </form>
          </div>
        </Card>
      </FadeIn>
      
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent size="sm">
          <DialogHeader>
            <DialogTitle>Success!</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <p className="text-muted-foreground">
              Your content plan has been created successfully.
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDialog(false)}>
              Close
            </Button>
            <Button onClick={() => setShowDialog(false)}>
              View Plan
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}