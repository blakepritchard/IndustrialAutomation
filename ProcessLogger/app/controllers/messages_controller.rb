class MessagesController < ApplicationController
  skip_before_filter  :verify_authenticity_token

  def show
    @message = Message.find(params[:id])
  end

  def new

  end

  def create
    # render plain: params[:message].inspect
    @message = Message.new(message_params)

    @message.save
    redirect_to(@message)
    send_alarms(@message)

  end

  protected
    def send_alarms(message)

      if @message.adc1 > 100
        require 'twilio-ruby'

        # put your own credentials here
        account_sid = 'ACcf3d9b19452bf652b424aec7f1e4c0d5'
        auth_token = 'a44f7f75644477c22b4d7be9169bf88d'

        # set up a client to talk to the Twilio REST API
        @client = Twilio::REST::Client.new account_sid, auth_token

        @client.account.messages.create({
                                            :from => '+14697895468',
                                            :to => '2145174227',
                                            :body => 'the value of ADC1 is now:'+@message.adc1.to_s,
                                        })

      end
    end


  private
    def message_params
      #params.require(:message).permit(:process, :sender, :text)
      params.permit(:process, :sender, :text, :adc1, :adc2, :adc3, :adc4, :adc5, :adc6, :adc7, :adc8)
    end

end
