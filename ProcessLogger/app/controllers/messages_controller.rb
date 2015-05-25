class MessagesController < ApplicationController
  skip_before_filter  :verify_authenticity_token

  def index
    @message = Message.all
  end

  def chart
  end

  def tension_graph
  end

  def chart_data
    @message = Message.last
    render json: [@message.id, @message.adc1]
  end

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
      require 'twilio-ruby'



      if @message.adc1 > 0.8
        # put your own credentials here
        account_sid = 'ACcf3d9b19452bf652b424aec7f1e4c0d5'
        auth_token = 'a44f7f75644477c22b4d7be9169bf88d'

        # set up a client to talk to the Twilio REST API
        @client = Twilio::REST::Client.new account_sid, auth_token

        @client.account.messages.create({
                                            :from => '+14697895468',
                                            :to => '2145174227',
                                            :body => 'the value of Tension is now:'<<@message.adc1.to_s,
                                        })
      elsif @message.adc1 > 0.65
        TensionMailer.sample_email(@message).deliver

      end
    end

    def send_sms(account_sid, auth_token, from, to, body)

    end

    def send_voice_message

    end

  private
    def message_params
      #params.require(:message).permit(:process, :sender, :text)
      params.permit(:process, :sender, :text, :adc1, :adc2, :adc3, :adc4, :adc5, :adc6, :adc7, :adc8)
    end

end
