/*
 * ex2.cc
 *
 *  Created on: 23-Apr-2024
 *      Author: Prashant Gode
 */

#include <string.h>
#include <omnetpp.h>

using namespace omnetpp;

class txc1 : public cSimpleModule
{
    private:
        simsignal_t arrivalSignal;
        int counter;
        simtime_t prev_msgTime;
        cMessage *event = nullptr;
        cMessage *tictocMsg = nullptr;
        cHistogram delayStats;

    public:
    virtual ~txc1();
    protected:
        virtual void initialize() override;
        virtual void handleMessage(cMessage *msg) override;
};

Define_Module(txc1);

txc1::~txc1()
{
    cancelAndDelete(event);
    delete tictocMsg;
}

void txc1::initialize()
{
    counter = 200;
    prev_msgTime = 0;
    arrivalSignal = registerSignal("arrival");
    WATCH(counter);

    event = new cMessage("event");
    tictocMsg = nullptr;

    if(strcmp("S", getName()) == 0){
        scheduleAt(0.0, event);
        tictocMsg = new cMessage("tictocMsg");
    }
}

void txc1::handleMessage(cMessage *msg)
{
    counter --;
    if (counter == 0) {
            EV << getName() << "Counter reached zero, deleting message\n";
            delete msg;
        }
        else {
            if (msg == event) {
                   EV << "Wait period is over, sending back message\n";
                   send(tictocMsg, "out");
                   tictocMsg = nullptr;
               }
               else {
                       simtime_t delay = par("delayTime");

                       EV << "Message arrived, starting to wait " << delay << " secs...\n";
                       tictocMsg = msg;
                       scheduleAt(simTime()+ par("delayTime"), event);

                       simtime_t curr_time = simTime(), interarrTime = curr_time - prev_msgTime;
                       emit(arrivalSignal, interarrTime);
                      prev_msgTime = curr_time;


                   }
               }

}


