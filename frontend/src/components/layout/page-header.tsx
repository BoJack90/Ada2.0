'use client'

import Link from 'next/link'
import { Filter, Calendar, ChevronRight } from 'lucide-react'

interface PageHeaderProps {
  title: string
  subtitle?: string
  breadcrumbs?: Array<{
    label: string
    href?: string
  }>
  actions?: React.ReactNode
}

export function PageHeader({ title, subtitle, breadcrumbs = [], actions }: PageHeaderProps) {
  return (
    <div className="page-header">
      <div className="page-header-left d-flex align-items-center">
        <div className="page-header-title">
          <h5 className="m-b-10">{title}</h5>
          {subtitle && <p className="text-muted fs-13">{subtitle}</p>}
        </div>
        {breadcrumbs.length > 0 && (
          <ul className="breadcrumb">
            {breadcrumbs.map((crumb, index) => (
              <li key={index} className="breadcrumb-item">
                {crumb.href && index !== breadcrumbs.length - 1 ? (
                  <Link href={crumb.href}>{crumb.label}</Link>
                ) : (
                  <span>{crumb.label}</span>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
      
      {actions && (
        <div className="page-header-right ms-auto">
          <div className="page-header-right-items">
            <div className="d-flex d-md-none">
              <button className="page-header-right-close-toggle">
                <ChevronRight className="me-2" size={16} />
                <span>Back</span>
              </button>
            </div>
            <div className="d-flex align-items-center gap-2 page-header-right-items-wrapper">
              {actions}
            </div>
          </div>
          <div className="d-md-none d-flex align-items-center">
            <button className="page-header-right-open-toggle">
              <Filter size={20} />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// Common action components for reuse
export function DateRangePicker() {
  return (
    <div id="reportrange" className="reportrange-picker d-flex align-items-center">
      <Calendar size={16} className="me-2" />
      <span className="reportrange-picker-field">Last 30 days</span>
    </div>
  )
}

export function FilterDropdown() {
  return (
    <div className="dropdown filter-dropdown">
      <button 
        className="btn btn-light-brand" 
        data-bs-toggle="dropdown" 
        data-bs-offset="0, 10" 
        data-bs-auto-close="outside"
      >
        <Filter size={16} className="me-2" />
        <span>Filter</span>
      </button>
      <div className="dropdown-menu dropdown-menu-end">
        <div className="dropdown-item">
          <div className="custom-control custom-checkbox">
            <input type="checkbox" className="custom-control-input" id="Active" defaultChecked />
            <label className="custom-control-label c-pointer" htmlFor="Active">Active</label>
          </div>
        </div>
        <div className="dropdown-item">
          <div className="custom-control custom-checkbox">
            <input type="checkbox" className="custom-control-input" id="Inactive" />
            <label className="custom-control-label c-pointer" htmlFor="Inactive">Inactive</label>
          </div>
        </div>
        <div className="dropdown-divider"></div>
        <button className="dropdown-item">
          <Filter className="me-3" size={16} />
          <span>Manage Filters</span>
        </button>
      </div>
    </div>
  )
}
