import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  skipTrailingSlashRedirect: true,
  async rewrites() {
    const apiBaseUrl = process.env.BACKEND_API_BASE_URL;

    if (!apiBaseUrl) {
      return [];
    }

    return [
      {
        source: '/api/token/',
        destination: `${apiBaseUrl}/api/token/`,
      },
      {
        source: '/api/token/refresh/',
        destination: `${apiBaseUrl}/api/token/refresh/`,
      },
      {
        source: '/api/v1/me/',
        destination: `${apiBaseUrl}/api/v1/me/`,
      },
      {
        source: '/api/v1/reports/executive-summary/',
        destination: `${apiBaseUrl}/api/v1/reports/executive-summary/`,
      },
      {
        source: '/api/v1/contexts/',
        destination: `${apiBaseUrl}/api/v1/contexts/`,
      },
      {
        source: '/api/v1/contexts/:id/',
        destination: `${apiBaseUrl}/api/v1/contexts/:id/`,
      },
      {
        source: '/api/v1/sites/',
        destination: `${apiBaseUrl}/api/v1/sites/`,
      },
      {
        source: '/api/v1/users/',
        destination: `${apiBaseUrl}/api/v1/users/`,
      },
      {
        source: '/api/v1/departments/',
        destination: `${apiBaseUrl}/api/v1/departments/`,
      },
      {
        source: '/api/v1/tasks/',
        destination: `${apiBaseUrl}/api/v1/tasks/`,
      },
      {
        source: '/api/v1/tasks/:id/',
        destination: `${apiBaseUrl}/api/v1/tasks/:id/`,
      },
      {
        source: '/api/v1/tasks/:id/:action/',
        destination: `${apiBaseUrl}/api/v1/tasks/:id/:action/`,
      },
      {
        source: '/api/v1/documents/',
        destination: `${apiBaseUrl}/api/v1/documents/`,
      },
      {
        source: '/api/v1/documents/:id/',
        destination: `${apiBaseUrl}/api/v1/documents/:id/`,
      },
      {
        source: '/api/v1/evidence/',
        destination: `${apiBaseUrl}/api/v1/evidence/`,
      },
      {
        source: '/api/v1/evidence/:id/',
        destination: `${apiBaseUrl}/api/v1/evidence/:id/`,
      },
      {
        source: '/api/v1/evidence/:id/accept/',
        destination: `${apiBaseUrl}/api/v1/evidence/:id/accept/`,
      },
      {
        source: '/api/v1/contracts/templates/',
        destination: `${apiBaseUrl}/api/v1/contracts/templates/`,
      },
      {
        source: '/api/v1/contracts/records/',
        destination: `${apiBaseUrl}/api/v1/contracts/records/`,
      },
      {
        source: '/api/v1/contracts/records/:id/:action/',
        destination: `${apiBaseUrl}/api/v1/contracts/records/:id/:action/`,
      },
      {
        source: '/api/v1/contracts/signatures/',
        destination: `${apiBaseUrl}/api/v1/contracts/signatures/`,
      },
      {
        source: '/api/v1/contracts/signatures/:id/sign/',
        destination: `${apiBaseUrl}/api/v1/contracts/signatures/:id/sign/`,
      },
      {
        source: '/api/v1/suppliers/',
        destination: `${apiBaseUrl}/api/v1/suppliers/`,
      },
      {
        source: '/api/v1/suppliers/:id/:action/',
        destination: `${apiBaseUrl}/api/v1/suppliers/:id/:action/`,
      },
      {
        source: '/api/v1/suppliers/documents/',
        destination: `${apiBaseUrl}/api/v1/suppliers/documents/`,
      },
      {
        source: '/api/v1/suppliers/documents/:id/:action/',
        destination: `${apiBaseUrl}/api/v1/suppliers/documents/:id/:action/`,
      },
      {
        source: '/api/v1/suppliers/engagements/',
        destination: `${apiBaseUrl}/api/v1/suppliers/engagements/`,
      },
      {
        source: '/api/v1/suppliers/payment-packs/',
        destination: `${apiBaseUrl}/api/v1/suppliers/payment-packs/`,
      },
      {
        source: '/api/v1/suppliers/payment-packs/:id/send-to-erp/',
        destination: `${apiBaseUrl}/api/v1/suppliers/payment-packs/:id/send-to-erp/`,
      },
      {
        source: '/api/v1/artists/',
        destination: `${apiBaseUrl}/api/v1/artists/`,
      },
      {
        source: '/api/v1/artists/documents/',
        destination: `${apiBaseUrl}/api/v1/artists/documents/`,
      },
      {
        source: '/api/v1/artists/documents/:id/:action/',
        destination: `${apiBaseUrl}/api/v1/artists/documents/:id/:action/`,
      },
      {
        source: '/api/v1/artists/engagements/',
        destination: `${apiBaseUrl}/api/v1/artists/engagements/`,
      },
      {
        source: '/api/v1/artists/engagements/:id/confirm/',
        destination: `${apiBaseUrl}/api/v1/artists/engagements/:id/confirm/`,
      },
      {
        source: '/api/v1/marketing/campaigns/',
        destination: `${apiBaseUrl}/api/v1/marketing/campaigns/`,
      },
      {
        source: '/api/v1/marketing/campaigns/:id/:action/',
        destination: `${apiBaseUrl}/api/v1/marketing/campaigns/:id/:action/`,
      },
      {
        source: '/api/v1/marketing/deliverables/',
        destination: `${apiBaseUrl}/api/v1/marketing/deliverables/`,
      },
      {
        source: '/api/v1/marketing/deliverables/:id/complete/',
        destination: `${apiBaseUrl}/api/v1/marketing/deliverables/:id/complete/`,
      },
      {
        source: '/api/v1/technical/riders/',
        destination: `${apiBaseUrl}/api/v1/technical/riders/`,
      },
      {
        source: '/api/v1/technical/riders/:id/:action/',
        destination: `${apiBaseUrl}/api/v1/technical/riders/:id/:action/`,
      },
      {
        source: '/api/v1/technical/crew/',
        destination: `${apiBaseUrl}/api/v1/technical/crew/`,
      },
      {
        source: '/api/v1/technical/equipment/',
        destination: `${apiBaseUrl}/api/v1/technical/equipment/`,
      },
      {
        source: '/api/v1/operations/foh-plans/',
        destination: `${apiBaseUrl}/api/v1/operations/foh-plans/`,
      },
      {
        source: '/api/v1/operations/foh-plans/:id/:action/',
        destination: `${apiBaseUrl}/api/v1/operations/foh-plans/:id/:action/`,
      },
      {
        source: '/api/v1/operations/checklists/',
        destination: `${apiBaseUrl}/api/v1/operations/checklists/`,
      },
      {
        source: '/api/v1/operations/checklists/:id/check/',
        destination: `${apiBaseUrl}/api/v1/operations/checklists/:id/check/`,
      },
      {
        source: '/api/v1/operations/incidents/',
        destination: `${apiBaseUrl}/api/v1/operations/incidents/`,
      },
      {
        source: '/api/v1/ticketing/setups/',
        destination: `${apiBaseUrl}/api/v1/ticketing/setups/`,
      },
      {
        source: '/api/v1/ticketing/setups/:id/:action/',
        destination: `${apiBaseUrl}/api/v1/ticketing/setups/:id/:action/`,
      },
      {
        source: '/api/v1/ticketing/sales-imports/',
        destination: `${apiBaseUrl}/api/v1/ticketing/sales-imports/`,
      },
      {
        source: '/api/v1/reports/department-readiness/:id/',
        destination: `${apiBaseUrl}/api/v1/reports/department-readiness/:id/`,
      },
      {
        source: '/api/v1/reports/youth-summary/:id/',
        destination: `${apiBaseUrl}/api/v1/reports/youth-summary/:id/`,
      },
      {
        source: '/api/v1/reports/audit-export/',
        destination: `${apiBaseUrl}/api/v1/reports/audit-export/`,
      },
      {
        source: '/api/v1/audit/',
        destination: `${apiBaseUrl}/api/v1/audit/`,
      },
      {
        source: '/api/v1/youth/projects/',
        destination: `${apiBaseUrl}/api/v1/youth/projects/`,
      },
      {
        source: '/api/v1/youth/projects/:id/:action/',
        destination: `${apiBaseUrl}/api/v1/youth/projects/:id/:action/`,
      },
      {
        source: '/api/v1/youth/activities/',
        destination: `${apiBaseUrl}/api/v1/youth/activities/`,
      },
      {
        source: '/api/v1/youth/sessions/',
        destination: `${apiBaseUrl}/api/v1/youth/sessions/`,
      },
      {
        source: '/api/v1/youth/sessions/:id/:action/',
        destination: `${apiBaseUrl}/api/v1/youth/sessions/:id/:action/`,
      },
      {
        source: '/api/v1/youth/learner-groups/',
        destination: `${apiBaseUrl}/api/v1/youth/learner-groups/`,
      },
      {
        source: '/api/v1/youth/facilitators/',
        destination: `${apiBaseUrl}/api/v1/youth/facilitators/`,
      },
      {
        source: '/api/v1/youth/facilitators/:id/vet/',
        destination: `${apiBaseUrl}/api/v1/youth/facilitators/:id/vet/`,
      },
      {
        source: '/api/v1/youth/consent/',
        destination: `${apiBaseUrl}/api/v1/youth/consent/`,
      },
      {
        source: '/api/v1/youth/consent/:id/:action/',
        destination: `${apiBaseUrl}/api/v1/youth/consent/:id/:action/`,
      },
      {
        source: '/api/v1/youth/attendance/',
        destination: `${apiBaseUrl}/api/v1/youth/attendance/`,
      },
      {
        source: '/api/v1/youth/assessments/',
        destination: `${apiBaseUrl}/api/v1/youth/assessments/`,
      },
      {
        source: '/api/v1/youth/showcases/',
        destination: `${apiBaseUrl}/api/v1/youth/showcases/`,
      },
      {
        source: '/api/v1/approvals/steps/',
        destination: `${apiBaseUrl}/api/v1/approvals/steps/`,
      },
      {
        source: '/api/v1/approvals/requests/',
        destination: `${apiBaseUrl}/api/v1/approvals/requests/`,
      },
      {
        source: '/api/v1/approvals/requests/:id/:action/',
        destination: `${apiBaseUrl}/api/v1/approvals/requests/:id/:action/`,
      },
      {
        source: '/api/v1/workflows/templates/',
        destination: `${apiBaseUrl}/api/v1/workflows/templates/`,
      },
      {
        source: '/api/v1/workflows/step-templates/',
        destination: `${apiBaseUrl}/api/v1/workflows/step-templates/`,
      },
      {
        source: '/api/v1/workflows/instances/',
        destination: `${apiBaseUrl}/api/v1/workflows/instances/`,
      },
      {
        source: '/api/v1/workflows/steps/',
        destination: `${apiBaseUrl}/api/v1/workflows/steps/`,
      },
      {
        source: '/api/v1/workflows/steps/:id/advance/',
        destination: `${apiBaseUrl}/api/v1/workflows/steps/:id/advance/`,
      },
      {
        source: '/api/v1/reports/context-readiness/:id/',
        destination: `${apiBaseUrl}/api/v1/reports/context-readiness/:id/`,
      },
      {
        source: '/api/:path*',
        destination: `${apiBaseUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
