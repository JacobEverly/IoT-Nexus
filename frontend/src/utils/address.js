export const isValidWalletAddress = (recipientWalletAddress) =>
  recipientWalletAddress?.startsWith("0x") &&
  recipientWalletAddress?.length === 42;

export const shortAddress = (addr) =>
  addr.length > 10 && addr.startsWith("0x")
    ? `${addr.substring(0, 6)}...${addr.substring(addr.length - 4)}`
    : addr;

export const mediumAddress = (addr) =>
  addr.length > 10 && addr.startsWith("0x")
    ? `${addr.substring(0, 15)}...${addr.substring(addr.length - 15)}`
    : addr;
