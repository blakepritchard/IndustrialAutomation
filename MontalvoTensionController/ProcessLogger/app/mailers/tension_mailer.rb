class TensionMailer < ActionMailer::Base
  default from: 'blakepritchard@gmail.com'

  def sample_email(message)
    @message = message
    mail(to: 'blakepritchard@gmail.com', subject: 'Sample Email')
  end
end
