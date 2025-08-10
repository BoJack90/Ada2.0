'use client'

import { motion } from 'framer-motion'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { PageHeader, DateRangePicker, FilterDropdown } from '@/components/layout/page-header'
import { StatCard, Card, MetricCard } from '@/components/ui/cards'
import { useOrganizationStore } from '@/stores'
import { OrganizationDashboard } from './organization-dashboard'
import { 
  Mail, 
  Send, 
  CheckCircle, 
  Eye, 
  MousePointer, 
  Users,
  TrendingUp,
  TrendingDown,
  Activity,
  DollarSign,
  ShoppingCart,
  BarChart3
} from 'lucide-react'

export function AnalyticsDashboard() {
  const { currentOrganization } = useOrganizationStore()

  const breadcrumbs = [
    { label: 'Home', href: '/' },
    { label: 'Analytics' }
  ]

  const headerActions = (
    <>
      <DateRangePicker />
      <FilterDropdown />
    </>
  )

  return (
    <DashboardLayout>
      {/* Modern Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="mb-8"
      >
        <div className="card-base p-8">
          <div className="flex items-center space-x-4 mb-4">
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.1, type: "spring", stiffness: 200 }}
              className="p-3 bg-primary/10 rounded-lg"
            >
              <BarChart3 className="h-8 w-8 text-primary" />
            </motion.div>
            <div>
              <h1 className="text-3xl font-bold text-foreground">
                {currentOrganization ? `Dashboard - ${currentOrganization.name}` : "Analytics Dashboard"}
              </h1>
              <p className="text-muted-foreground mt-2">Comprehensive business insights and performance metrics</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <DateRangePicker />
            <FilterDropdown />
          </div>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="main-content">
        {/* Jeśli jest wybrana organizacja, pokaż OrganizationDashboard */}
        {currentOrganization ? (
          <OrganizationDashboard />
        ) : (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
            className="space-y-6"
          >
            {/* Email Reports Section */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.2 }}
            >
              <div className="card-base overflow-hidden">
                <div className="px-6 py-4 border-b border-border">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Mail className="h-6 w-6 text-primary" />
                      <div>
                        <h2 className="text-xl font-semibold text-foreground">Email Reports</h2>
                        <p className="text-muted-foreground">Email Campaign Performance</p>
                      </div>
                    </div>
                    <button className="px-4 py-2 bg-primary/10 text-primary rounded-md hover:bg-primary/20 transition-colors">
                      View All
                    </button>
                  </div>
                </div>
                
                <div className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
                    <StatCard
                      title="Total Email"
                      value="50,545"
                      icon={Mail}
                      color="primary"
                    />
                    <StatCard
                      title="Email Sent"
                      value="25,000"
                      icon={Send}
                      color="warning"
                    />
                    <StatCard
                      title="Emails Delivered"
                      value="20,354"
                      icon={CheckCircle}
                      color="success"
                    />
                    <StatCard
                      title="Emails Opened"
                      value="12,422"
                      icon={Eye}
                      color="indigo"
                    />
                    <StatCard
                      title="Click Rate"
                      value="8,542"
                      icon={MousePointer}
                      color="danger"
                    />
                    <StatCard
                      title="Bounce Rate"
                      value="2.5%"
                      icon={TrendingDown}
                      color="warning"
                    />
                  </div>
                </div>
              </div>
            </motion.div>

          {/* Analytics Overview */}
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.3 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-6"
          >
            <div className="lg:col-span-2">
              <div className="card-base overflow-hidden">
                <div className="px-6 py-4 border-b border-border">
                  <div className="flex items-center space-x-3">
                    <Activity className="h-6 w-6 text-primary" />
                    <div>
                      <h2 className="text-xl font-semibold text-foreground">Traffic Analytics</h2>
                      <p className="text-muted-foreground">Website traffic overview</p>
                    </div>
                  </div>
                </div>
                
                <div className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                    <MetricCard
                      title="Total Visitors"
                      value="45,827"
                      change={{
                        value: 12.5,
                        period: "last month",
                        isPositive: true
                      }}
                      color="primary"
                    />
                    <MetricCard
                      title="Page Views"
                      value="123,456"
                      change={{
                        value: 8.2,
                        period: "last month",
                        isPositive: true
                      }}
                      color="success"
                    />
                    <MetricCard
                      title="Bounce Rate"
                      value="35.2%"
                      change={{
                        value: 2.1,
                        period: "last month",
                        isPositive: false
                      }}
                      color="warning"
                    />
                    <MetricCard
                      title="Conversion Rate"
                      value="3.8%"
                      change={{
                        value: 0.5,
                        period: "last month",
                        isPositive: true
                      }}
                      color="info"
                    />
                  </div>
                  
                  {/* Chart Placeholder */}
                  <div className="bg-muted/50 rounded-lg p-8 text-center border border-border">
                    <motion.div
                      initial={{ scale: 0.9, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ delay: 0.4, duration: 0.3 }}
                    >
                      <Activity size={48} className="text-primary/50 mb-4 mx-auto" />
                      <p className="text-foreground font-medium">Traffic Chart Placeholder</p>
                      <small className="text-muted-foreground">Chart component will be implemented here</small>
                    </motion.div>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <div className="card-base overflow-hidden">
                <div className="px-6 py-4 border-b border-border">
                  <div className="flex items-center space-x-3">
                    <TrendingUp className="h-6 w-6 text-primary" />
                    <div>
                      <h2 className="text-xl font-semibold text-foreground">Quick Stats</h2>
                      <p className="text-muted-foreground">Key performance indicators</p>
                    </div>
                  </div>
                </div>
                
                <div className="p-6 space-y-4">
                  <motion.div 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 }}
                    className="flex items-center justify-between p-4 bg-primary/5 rounded-lg border border-primary/20"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-primary text-primary-foreground rounded-md">
                        <Users size={16} />
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900">Active Users</div>
                        <div className="text-sm text-gray-500">Currently online</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-gray-900">1,234</div>
                      <div className="text-sm text-green-600">+5.2%</div>
                    </div>
                  </motion.div>

                  <motion.div 
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 }}
                    className="flex items-center justify-between p-4 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl border border-emerald-100"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-emerald-500 text-white rounded-lg">
                        <DollarSign size={16} />
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900">Revenue</div>
                        <div className="text-sm text-gray-500">This month</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-gray-900">$12,456</div>
                      <div className="text-sm text-green-600">+12.8%</div>
                    </div>
                  </motion.div>

                  <motion.div 
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.7 }}
                    className="flex items-center justify-between p-4 bg-gradient-to-r from-orange-50 to-yellow-50 rounded-xl border border-orange-100"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-orange-500 text-white rounded-lg">
                        <ShoppingCart size={16} />
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900">Orders</div>
                        <div className="text-sm text-gray-500">Total this week</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-gray-900">892</div>
                      <div className="text-sm text-red-600">-2.1%</div>
                    </div>
                  </motion.div>

                  <motion.div 
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.8 }}
                    className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl border border-purple-100"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-purple-500 text-white rounded-lg">
                        <TrendingUp size={16} />
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900">Growth Rate</div>
                        <div className="text-sm text-gray-500">Monthly average</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-gray-900">18.5%</div>
                      <div className="text-sm text-green-600">+3.2%</div>
                    </div>
                  </motion.div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Recent Activity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
              <div className="bg-gradient-to-r from-purple-500 to-pink-600 p-6 text-white">
                <div className="flex items-center space-x-3">
                  <Activity className="h-6 w-6" />
                  <div>
                    <h2 className="text-xl font-semibold">Recent Activity</h2>
                    <p className="text-purple-100">Latest system activities</p>
                  </div>
                </div>
              </div>
              
              <div className="p-6">
                <div className="space-y-4">
                  <motion.div 
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 }}
                    className="flex items-center space-x-4 p-4 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100"
                  >
                    <div className="p-2 bg-blue-500 text-white rounded-lg">
                      <Users size={16} />
                    </div>
                    <div className="flex-grow">
                      <div className="font-semibold text-gray-900">New user registration</div>
                      <div className="text-sm text-gray-500">john.doe@example.com registered</div>
                    </div>
                    <div className="text-sm text-gray-400">2 min ago</div>
                  </motion.div>
                  
                  <motion.div 
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.7 }}
                    className="flex items-center space-x-4 p-4 rounded-xl bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-100"
                  >
                    <div className="p-2 bg-emerald-500 text-white rounded-lg">
                      <DollarSign size={16} />
                    </div>
                    <div className="flex-grow">
                      <div className="font-semibold text-gray-900">Payment received</div>
                      <div className="text-sm text-gray-500">$1,250 payment from client</div>
                    </div>
                    <div className="text-sm text-gray-400">15 min ago</div>
                  </motion.div>
                  
                  <motion.div 
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.8 }}
                    className="flex items-center space-x-4 p-4 rounded-xl bg-gradient-to-r from-orange-50 to-yellow-50 border border-orange-100"
                  >
                    <div className="p-2 bg-orange-500 text-white rounded-lg">
                      <Mail size={16} />
                    </div>
                    <div className="flex-grow">
                      <div className="font-semibold text-gray-900">Email campaign sent</div>
                      <div className="text-sm text-gray-500">Newsletter sent to 5,234 subscribers</div>
                    </div>
                    <div className="text-sm text-gray-400">1 hour ago</div>
                  </motion.div>
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
          )}
      </div>
    </DashboardLayout>
  )
}
