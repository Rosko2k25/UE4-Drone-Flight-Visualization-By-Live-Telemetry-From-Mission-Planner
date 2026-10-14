#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MAVLinkParser.generated.h"  // this must stay here

extern "C" {
#include "ardupilotmega/mavlink.h"
}

UCLASS(Blueprintable)
class MYPROJECT_API UMAVLinkParser : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable)
    void ParseBytes(const TArray<uint8>& ByteArray);
};