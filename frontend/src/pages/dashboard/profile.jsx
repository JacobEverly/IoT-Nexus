import {
  Card,
  CardBody,
  CardHeader,
  CardFooter,
  Avatar,
  Typography,
  Tabs,
  TabsHeader,
  Tab,
  Switch,
  Tooltip,
  Button,
  Progress,
} from "@material-tailwind/react";
import {
  HomeIcon,
  ChatBubbleLeftEllipsisIcon,
  Cog6ToothIcon,
  PencilIcon,
} from "@heroicons/react/24/solid";
import Blockies from 'react-blockies';
import { getMessages } from "@/restApis/getMessages";
import "@/../public/css/tailwind.css";
let messages = await getMessages();
let validator_address = null;
while (validator_address == null) {
  for (let i = 0; i < messages.length; i++) {
    if (messages[i].signed_validators.length > 0) {
      validator_address = messages[i].signed_validators[0].wallet_address;
      break;
    }
  }
}
let total_weight = 0;
let num_v = 0;
messages.map(({ signed_validators }, key) => {
  signed_validators.map(({ weight }, key) => {
    total_weight += weight;
  })
  num_v += 1;
  total_weight = total_weight / num_v;
})
function SignComponent({ signed_validators, validator_address }) {
  let signed = false;
  signed_validators.map(({ wallet_address }, key) => {
    if (wallet_address == validator_address) {
      signed = true;
    }
  })
  if (!signed) {
    return (
      <div className="container"><Button color="green" size="">Approve</Button> </div>
    )
  } else {
    return (
      <div><Button disabled color="light-green">Signed</Button></div>
    )
  }
}
function getCompletionRate(signed_validators) {
  let signed_weight = 0;
  signed_validators.map(({ weight }, key) => {
    signed_weight += weight;
  })
  let rate = signed_weight / total_weight;
  while (rate > 1) {
    rate /= 10;
  }
  return rate.toPrecision(2);
}
export function UserData() {
  return (
    <>
      <div className="relative mt-8 h-72 w-full overflow-hidden rounded-xl bg-[url(https://images.unsplash.com/photo-1531512073830-ba890ca4eba2?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80)] bg-cover	bg-center">
        <div className="absolute inset-0 h-full w-full bg-blue-500/50" />
      </div>
      <Card className="mx-3 -mt-16 mb-6 lg:mx-4">
        <CardBody className="p-4">
          <div className="mb-10 flex items-center justify-between gap-6">
            <div className="flex items-center gap-6">
              <Blockies
                data-testid="avatar"
                seed={validator_address.toLowerCase() || ""}
                scale={7}
                size={7}
              />
              <div>
                <Typography variant="h6" color="blue-gray" className="mb-1">
                  {validator_address}
                </Typography>
              </div>
            </div>
            {/* <div className="w-96"> */}
            {/* <Tabs value="app">
                <TabsHeader>
                  <Tab value="app">
                    <HomeIcon className="-mt-1 mr-2 inline-block h-5 w-5" />
                    App
                  </Tab>
                  <Tab value="message">
                    <ChatBubbleLeftEllipsisIcon className="-mt-0.5 mr-2 inline-block h-5 w-5" />
                    Message
                  </Tab>
                  <Tab value="settings">
                    <Cog6ToothIcon className="-mt-1 mr-2 inline-block h-5 w-5" />
                    Settings
                  </Tab>
                </TabsHeader>
              </Tabs> */}
            {/* </div> */}
          </div>
          <div className="gird-cols-1 mb-12 grid gap-12 px-4 lg:grid-cols-2 xl:grid-cols-3">
            <div>
              <Typography variant="h6" color="blue-gray" className="mb-3">
                Generate Your Message
              </Typography>

            </div>
            {/* <ProfileInfoCard
              title="Profile Information"
              description="Hi, I'm Alec Thompson, Decisions: If you can't decide, the answer is no. If two equally difficult paths, choose the one more painful in the short term (pain avoidance is creating an illusion of equality)."
              details={{
                "first name": "Alec M. Thompson",
                mobile: "(44) 123 1234 123",
                email: "alecthompson@mail.com",
                location: "USA",
                social: (
                  <div className="flex items-center gap-4">
                    <i className="fa-brands fa-facebook text-blue-700" />
                    <i className="fa-brands fa-twitter text-blue-400" />
                    <i className="fa-brands fa-instagram text-purple-500" />
                  </div>
                ),
              }}
              action={
                <Tooltip content="Edit Profile">
                  <PencilIcon className="h-4 w-4 cursor-pointer text-blue-gray-500" />
                </Tooltip>
              }
            /> */}
            {/* <div>
              <Typography variant="h6" color="blue-gray" className="mb-3">
                Platform Settings
              </Typography>
              <ul className="flex flex-col gap-6">
                {conversationsData.map((props) => (
                  <MessageCard
                    key={props.name}
                    {...props}
                    action={
                      <Button variant="text" size="sm">
                        reply
                      </Button>
                    }
                  />
                ))}
              </ul>
            </div> */}
          </div>
          <div className="px-4 pb-4">
            <Typography variant="h6" color="blue-gray" className="mb-2">
              Your Data
            </Typography>
            <CardBody className="overflow-x-scroll px-0 pt-0 pb-2">
              <table className="w-full min-w-[640px] table-auto">
                <thead>
                  <tr>
                    {["messages", "members", "company", "completion", "create at", "decision"].map(
                      (el) => (
                        <th
                          key={el}
                          className="border-b border-blue-gray-50 py-3 px-6 text-left"
                        >
                          <Typography
                            variant="small"
                            className="text-[11px] font-medium uppercase text-blue-gray-400"
                          >
                            {el}
                          </Typography>
                        </th>
                      )
                    )}
                  </tr>
                </thead>
                <tbody>
                  {messages.map(
                    ({ message, signed_validators, created_by, created_at }, key) => {
                      const className = `py-3 px-5 ${key === messages.length - 1
                        ? ""
                        : "border-b border-blue-gray-50"
                        }`;

                      return (
                        <tr key={message}>
                          <td className={className}>
                            <div className="flex items-center gap-4">

                              {/* <Avatar src={img} alt={message} size="sm" /> */}
                              <Typography
                                variant="small"
                                color="blue-gray"
                                className="font-bold"
                              >
                                {message}
                              </Typography>
                            </div>
                          </td>
                          <td className={`${className}`}>
                            <div className="members-container">
                              {signed_validators.map(({ wallet_address, weight }, key) => (
                                <Tooltip key={wallet_address} content={wallet_address}>
                                  {/* <Avatar
                                src={img}
                                alt={name}
                                size="xs"
                                variant="circular"
                                className={`cursor-pointer border-2 border-white ${
                                  key === 0 ? "" : "-ml-2.5"
                                }`}
                              /> */}
                                  <Blockies
                                    data-testid="avatar"
                                    seed={wallet_address.toLowerCase() || ""}
                                    scale={5}
                                    size={3}
                                    className="rounded-full"
                                  />
                                </Tooltip>
                              ))}
                            </div>
                          </td>
                          <td className={`${className}`}>
                            <div className="container">
                              <Blockies
                                data-testid="avatar"
                                seed={created_by.toLowerCase() || ""}
                                scale={5}
                                size={5}
                                className="rounded-full"
                              />
                              <Typography
                                variant="small"
                                className="text-xs font-medium text-blue-gray-600"
                                style={{ paddingLeft: "10px" }}
                              >
                                {created_by}
                              </Typography>
                            </div>
                          </td>
                          <td className={className}>
                            <div className="w-10/12">
                              <Typography
                                variant="small"
                                className="mb-1 block text-xs font-medium text-blue-gray-600"
                              >
                                {getCompletionRate(signed_validators) * 100}%
                              </Typography>
                              <Progress
                                value={100}
                                variant="gradient"
                                color={99 === 100 ? "green" : "blue"}
                                className="h-1"
                              />
                            </div>
                          </td>
                          <td className={className}>
                            <Typography
                              variant="small"
                              className="text-xs font-medium text-blue-gray-600"
                            >
                              {created_at}
                            </Typography>
                          </td>
                          <td className={`flex-center-wrap ${className}`}>
                            <SignComponent signed_validators={signed_validators} validator_address={validator_address} />
                          </td>
                        </tr>
                      );
                    }
                  )}
                </tbody>
              </table>
            </CardBody>
          </div>
        </CardBody>
      </Card>
    </>
  );
}

export default UserData;
