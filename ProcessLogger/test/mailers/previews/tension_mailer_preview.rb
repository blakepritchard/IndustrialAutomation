# Preview all emails at http://localhost:3000/rails/mailers/tension_mailer
class TensionMailerPreview < ActionMailer::Preview
  def sample_mail_preview
    @message = Message.last
    TensionMailer.sample_email(@message)
  end
end
