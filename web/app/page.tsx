import { ProtocolApp } from "./protocol-app";
import { PROTOCOL_DESCRIPTOR } from "../lib/protocol";

export default function Home() {
  return <ProtocolApp descriptor={PROTOCOL_DESCRIPTOR} />;
}
