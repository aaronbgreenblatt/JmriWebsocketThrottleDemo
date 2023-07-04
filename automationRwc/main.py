from jmriConnector import jmriConnector
import config

def main():
    jc = jmriConnector.jmriConnector(config.JMRI_WEB_SERVER_ADDRESS, config.JRMI_WEB_SERVER_PORT)

    
    reporters = jc.list_reporters()
    #print("Reporters: " + str(reporters))

    reporter_state = jc.get_reporter_state("MR001")
    #print("Reporter MR001: " + str(reporter_state))

    jc.run_train(138, 0.5, "forward")



if __name__ == "__main__":
    main()