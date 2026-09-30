// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/home', name: 'Home', component: () => import('@/views/Home.vue') },
  { path: '/login', name: 'Login', component: () => import('@/views/auth/Login.vue') },
  { path: '/register/student', name: 'RegisterStudent', component: () => import('@/views/auth/RegisterStudent.vue') },
  { path: '/register/company', name: 'RegisterCompany', component: () => import('@/views/auth/RegisterCompany.vue') },

  // Admin
  { path: '/admin', name: 'AdminDashboard', component: () => import('@/views/admin/Dashboard.vue'), meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/companies', name: 'AdminCompanies', component: () => import('@/views/admin/Companies.vue'), meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/companies/:id/profile', name: 'AdminCompanyDetail', component: () => import('@/views/admin/CompanyDetail.vue'), meta: { requiresAuth: true, role: 'admin' }, props: true },
  { path: '/admin/companies/:id/reports', name: 'AdminCompanyReport', component: () => import('@/views/admin/CompanyReport.vue'), meta: { requiresAuth: true, role: 'admin' }, props: true },
  { path: '/admin/students', name: 'AdminStudents', component: () => import('@/views/admin/Students.vue'), meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/students/:id/profile', name: 'AdminStudentDetail', component: () => import('@/views/admin/StudentDetail.vue'), meta: { requiresAuth: true, role: 'admin' }, props: true },
  { path: '/admin/students/:id/reports', name: 'AdminStudentReport', component: () => import('@/views/admin/StudentReport.vue'), meta: { requiresAuth: true, role: 'admin' }, props: true },
  { path: '/admin/drives', name: 'AdminDrives', component: () => import('@/views/admin/Drives.vue'), meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/applications', name: 'AdminApplications', component: () => import('@/views/admin/Applications.vue'), meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/reports', name: 'AdminReports', component: () => import('@/views/admin/Reports.vue'), meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/settings', name: 'AdminSettings', component: () => import('@/views/admin/Settings.vue'), meta: { requiresAuth: true, role: 'admin' } },

  // Company
  { path: '/company', name: 'CompanyDashboard', component: () => import('@/views/company/Dashboard.vue'), meta: { requiresAuth: true, role: 'company' } },
  { path: '/company/profile', name: 'CompanyProfile', component: () => import('@/views/company/Profile.vue'), meta: { requiresAuth: true, role: 'company' } },
  { path: '/company/drives', name: 'CompanyDrives', component: () => import('@/views/company/Drives.vue'), meta: { requiresAuth: true, role: 'company' } },
  { path: '/company/drives/new', name: 'CompanyDriveNew', component: () => import('@/views/company/DriveForm.vue'), meta: { requiresAuth: true, role: 'company' } },
  { path: '/company/drives/:id/edit', name: 'CompanyDriveEdit', component: () => import('@/views/company/DriveForm.vue'), meta: { requiresAuth: true, role: 'company' }, props: true },
  { path: '/company/drives/:id/applications', name: 'CompanyDriveApplications', component: () => import('@/views/company/DriveApplications.vue'), meta: { requiresAuth: true, role: 'company' }, props: true },
  { path: '/company/reports', name: 'CompanyReports', component: () => import('@/views/company/Reports.vue'), meta: { requiresAuth: true, role: 'company' } },

  // Student
  { path: '/student', name: 'StudentDashboard', component: () => import('@/views/student/Dashboard.vue'), meta: { requiresAuth: true, role: 'student' } },
  { path: '/student/profile', name: 'StudentProfile', component: () => import('@/views/student/Profile.vue'), meta: { requiresAuth: true, role: 'student' } },
  { path: '/student/companies', name: 'StudentCompanies', component: () => import('@/views/student/Companies.vue'), meta: { requiresAuth: true, role: 'student' } },
  { path: '/student/drives', name: 'StudentDrives', component: () => import('@/views/student/Drives.vue'), meta: { requiresAuth: true, role: 'student' } },
  { path: '/student/reports', name: 'StudentReports', component: () => import('@/views/student/Reports.vue'), meta: { requiresAuth: true, role: 'student' } },
  { path: '/student/drives/:id', name: 'StudentDriveDetail', component: () => import('@/views/student/DriveDetail.vue'), meta: { requiresAuth: true, role: 'student' }, props: true },
  { path: '/student/applications', name: 'StudentApplications', component: () => import('@/views/student/Applications.vue'), meta: { requiresAuth: true, role: 'student' } },
  { path: '/student/applications/:id', name: 'StudentApplicationDetail', component: () => import('@/views/student/ApplicationDetail.vue'), meta: { requiresAuth: true, role: 'student' }, props: true },

  // Shared
  { path: '/companies/:id', name: 'CompanyPublicProfile', component: () => import('@/views/shared/CompanyPublicProfile.vue'), meta: { requiresAuth: true }, props: true },

  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/views/NotFound.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() { return { top: 0 } }
})

function homeForRole(role) {
  if (role === 'admin') return '/admin'
  if (role === 'company') return '/company'
  if (role === 'student') return '/student'
  return '/home'
}

router.beforeEach(async (to) => {
  if (!store.state.auth.ready) {
    await store.dispatch('auth/fetchUser')
  }
  const isLoggedIn = store.getters['auth/isLoggedIn']
  const role = store.getters['auth/role']

  if ((to.name === 'Login' || to.name === 'RegisterStudent' || to.name === 'RegisterCompany') && isLoggedIn) {
    return homeForRole(role)
  }
  if (to.meta.requiresAuth && !isLoggedIn) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }
  if (to.meta.role && to.meta.role !== role) {
    return isLoggedIn ? homeForRole(role) : { name: 'Login' }
  }
  return true
})

export default router
