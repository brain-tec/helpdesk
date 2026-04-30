from odoo import api, models
from odoo.tools import email_normalize


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def _message_route_process(self, message, message_dict, routes):
        self.change_ticket_status_via_mail(routes, message_dict)
        return super()._message_route_process(message, message_dict, routes)

    def change_ticket_status_via_mail(self, routes, message_dict):
        if routes and routes[0][0] == "helpdesk.ticket":
            ticket_id = routes[0][1]
            email_from = message_dict.get("email_from")
            if email_from:
                email_from = email_normalize(email_from)

            if ticket_id:
                ticket = self.env["helpdesk.ticket"].sudo().browse(int(ticket_id))
                if ticket and routes[0][3]:
                    partner_id = (
                        self.env["res.users"]
                        .search([("id", "=", routes[0][3])], limit=1)
                        .partner_id.id
                    )
                    partner_matches = partner_id and partner_id == ticket.partner_id.id
                    partner_email_matches = ticket.partner_id.email == email_from
                    if (
                        (partner_matches or partner_email_matches)
                        and ticket.team_id.autoupdate_ticket_stage
                        and ticket.stage_id in ticket.team_id.autopupdate_src_stage_ids
                    ):
                        ticket.stage_id = ticket.team_id.autopupdate_dest_stage_id.id
