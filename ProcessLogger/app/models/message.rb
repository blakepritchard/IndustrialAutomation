class Message < ActiveRecord::Base
  validates :process, :presence => true
  validates :sender, :presence => true

  after_validation :send_alarms

  protected
    def send_alarms
      if self.adc1 > 100
        require 'twilio-ruby'

        # put your own credentials here
        account_sid = 'ACcf3d9b19452bf652b424aec7f1e4c0d5'
        auth_token = 'a44f7f75644477c22b4d7be9169bf88d'

        # set up a client to talk to the Twilio REST API
        @client = Twilio::REST::Client.new account_sid, auth_token

        @client.account.messages.create({
                                            :from => '+14697895468',
                                            :to => '2145174227',
                                            :body => 'the roof is on fire, Again!',
                                        })

      end
    end


end
