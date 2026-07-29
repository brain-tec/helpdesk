from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def _message_route_process(self, message, message_dict, routes):
        if not self._skip_ticket_stage_update_from_autoreply(
            message, message_dict, routes
        ):
            self.change_status_ticket_from_portal(routes)
        return super()._message_route_process(message, message_dict, routes)

    def _skip_ticket_stage_update_from_autoreply(self, message, message_dict, routes):
        """Return True to suppress stage updates triggered by auto-reply emails.

        Override in integration modules to implement auto-reply detection.
        Returns False by default so no update is suppressed.
        """
        return False

    def change_status_ticket_from_portal(self, routes):
        if routes and routes[0][0] == "helpdesk.ticket":
            ticket_id = routes[0][1]
            if ticket_id:
                ticket = self.env["helpdesk.ticket"].sudo().browse(int(ticket_id))
                if ticket and routes[0][3]:
                    partner_id = (
                        self.env["res.users"]
                        .search([("id", "=", routes[0][3])], limit=1)
                        .partner_id.id
                    )
                    if partner_id:
                        if (
                            ticket
                            and partner_id == ticket.partner_id.id
                            and ticket.team_id.autoupdate_ticket_stage
                            and ticket.stage_id
                            in ticket.team_id.autopupdate_src_stage_ids
                        ):
                            ticket.stage_id = (
                                ticket.team_id.autopupdate_dest_stage_id.id
                            )
