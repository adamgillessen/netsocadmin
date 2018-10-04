# stdlib
import logging
# lib
import flask
# local
import help_post
import login_tools


__all__ = [
    "CompleteSudo",
    "Sudo",
]


class CompleteSudo(flask.views.View):
    """
    Route: /completesudoapplication
        This is run by the sudo-signup form in sudo.html.
        It will send an email to the SysAdmin team as well as to the discord server notifying us that a request for
            sudo on feynman has been made.
    """
    # Decorate all methods with this
    decorators = [login_tools.protected_page]
    # Logger instance
    logger = logging.getLogger("netsocadmin.completesudoapplication")
    # Specify which method(s) are allowed to be used to access the route
    methods = ["POST"]

    def render(self, error=False):
        """Render the template with appropriate messages for whether or not there's an error"""
        if error:
            caption = "There was a problem :("
            message = "Please email netsoc@uccsocieties.ie instead!"
        else:
            caption = "Success!"
            message = "A confirmation email has been sent to you. We will be in touch shortly."
        return flask.render_template(
            "message.html",
            show_logout_button=login_tools.is_logged_in(),
            caption=caption,
            message=message,
        )


    def dispatch_requests(self):
        self.logger.debug("Received request")
        # Get the details from the form data
        email = flask.request.form["email"]
        reason = flask.request.form["reason"]
        username = flask.session["username"]

        # Try to send the email
        try:
            help_post.send_sudo_request_email(username, email)
        except Exception as e:
            email_failed = True
            self.logger.error(f"Failed to send email: {str(e)}")

        # Try to send a message to the Discord
        try:
            subject = "Feynman Account Request"
            msg = f"This user wants an account on Feynman pls.\nReason: {reason}"
            help_post.send_help_bot(username, email, subject, msg)
        except Exception as e:
            discord_failed = True
            self.logger.error(f"Failed to send message to Discord: {str(e)}")

        # Return an appropriate response depending on whether or not the message sent
        return self.render(email_failed and discord_failed)


class Sudo(flask.views.View):
    """
    Route: /sudo
        This route will render the page for applying for sudo privilages.
    """
    # Decorate all methods with this
    decorators = [login_tools.protected_page]
    # Logger instance
    logger = logging.getLogger("netsocadmin.sudo")

    def dispatch_request(self):
        self.logger.debug("Received request")
        return flask.render_template(
            "sudo.html",
            show_logout_button=login_tools.is_logged_in(),
            username=flask.session["username"],
        )
