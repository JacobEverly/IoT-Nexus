import React from "react";
import {
  Typography,
  Card,
  CardHeader,
  CardBody,
  IconButton,
  Menu,
  MenuHandler,
  MenuList,
  MenuItem,
  Tooltip,
  Progress,
  Button
} from "@material-tailwind/react";
import {
  CheckIcon,
  EllipsisVerticalIcon,
} from "@heroicons/react/24/outline";
import "@/../public/css/tailwind.css";
import Blockies from 'react-blockies';
import { getMessages } from "@/restApis/getMessages";


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
export function ValidatePage() {
  console.log(messages);
  return (
    <div className="mt-12">
      <div className="mb-4 grid grid-cols-1 gap-6">
        <Card className="overflow-hidden xl:col-span-2">
          <CardHeader
            floated={false}
            shadow={false}
            color="transparent"
            className="m-0 flex items-center justify-between p-6"
          >
            <div>
              <Typography variant="h6" color="blue-gray" className="mb-1">
                Messages To Sign
              </Typography>
              <Typography
                variant="small"
                className="flex items-center gap-1 font-normal text-blue-gray-600"
              >
                <CheckIcon strokeWidth={3} className="h-4 w-4 text-blue-500" />
                <strong>30 done</strong> this month
              </Typography>
            </div>
            <Menu placement="left-start">
              <MenuHandler>
                <IconButton size="sm" variant="text" color="blue-gray">
                  <EllipsisVerticalIcon
                    strokeWidth={3}
                    fill="currenColor"
                    className="h-6 w-6"
                  />
                </IconButton>
              </MenuHandler>
              <MenuList>
                <MenuItem>Sort by Date</MenuItem>
                <MenuItem>Sort by Company</MenuItem>
              </MenuList>
            </Menu>
          </CardHeader>
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
        </Card>
      </div>
    </div >
  );
}

export default ValidatePage;
